/*
 * nccl_shm_shim.c — LD_PRELOAD shim to strip cudaHostRegisterMapped from
 * cudaHostRegister calls made by NCCL's SHM transport setup.
 *
 * Built with -nostdlib so the .so has ZERO glibc version requirements.
 * This allows the .so to load under any glibc (host or container).
 *
 *   cc -O2 -shared -fPIC -nostdlib -o nccl_shm_shim.so nccl_shm_shim.c
 *
 * We cannot use dlsym() without glibc, so we intercept by being loaded
 * before libcuda/libnccl and letting the real symbol resolve through the
 * normal PLT chain: declare the real function as a weak alias with a
 * different name, then call it.
 *
 * Actually the clean zero-dependency approach: use a GNU indirect function
 * (ifunc) resolver — the resolver runs before any glibc init, finds the
 * next definition of cudaHostRegister in the link map by walking the
 * auxiliary vector / DT_NEEDED, and returns its address.  That is complex.
 *
 * Simpler: use a .gnu_attribute + __asm__ .symver to pin the ONE glibc
 * symbol we actually need (dlsym) to the oldest available ABI (GLIBC_2.2.5).
 * dlsym has been at GLIBC_2.2.5 since the beginning — this is always
 * available on x86-64 Linux regardless of host or container glibc version.
 */

#define _GNU_SOURCE

/* Pin dlsym to GLIBC_2.2.5 — available on every x86-64 Linux since 2001.
 * This prevents the linker from recording a GLIBC_2.34 (or later) version
 * requirement in the .so even when compiling on a newer host.              */
__asm__(".symver dlsym,dlsym@GLIBC_2.2.5");

/* We only need these two declarations; avoid pulling in any headers. */
extern void *dlsym(void *handle, const char *symbol);
#define RTLD_NEXT ((void *)-1L)

typedef int cudaError_t;
#define CUDA_HOST_REGISTER_MAPPED 0x04u

typedef cudaError_t (*fn_t)(void*, __SIZE_TYPE__, unsigned int);
static fn_t real_fn;

cudaError_t cudaHostRegister(void *ptr, __SIZE_TYPE__ size, unsigned int flags) {
    if (!real_fn)
        real_fn = (fn_t) dlsym(RTLD_NEXT, "cudaHostRegister");
    flags &= ~CUDA_HOST_REGISTER_MAPPED;
    return real_fn(ptr, size, flags);
}
