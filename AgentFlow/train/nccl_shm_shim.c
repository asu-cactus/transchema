/*
 * nccl_shm_shim.c — LD_PRELOAD shim to strip cudaHostRegisterMapped from
 * cudaHostRegister calls made by NCCL's SHM transport setup.
 *
 * Build on the HOST (not inside the container) so it links against the
 * host's glibc.  Apptainer's LD_PRELOAD is resolved by the host dynamic
 * linker, so the .so must be compatible with the host libc.
 *
 *   cc -O2 -shared -fPIC -o nccl_shm_shim.so nccl_shm_shim.c -ldl
 *
 * Why this is needed
 * ------------------
 * NCCL's ncclShmOpen() always calls:
 *   cudaHostRegister(ptr, size, cudaHostRegisterPortable | cudaHostRegisterMapped)
 * even when CE mode (NCCL_SHM_USE_CUDA_MEMCPY=1) is active.
 * cudaHostRegisterMapped creates a GPU device mapping for the /dev/shm buffer
 * in the calling process's CUDA context.  Across separate Apptainer worker
 * processes, the NCCL init kernels attempt to access that cross-process device
 * address → "CUDA error: an illegal memory access was encountered".
 *
 * Fix: strip cudaHostRegisterMapped (bit 0x04).  cudaHostGetDevicePointer then
 * returns cudaErrorInvalidValue, dptr stays NULL.  NCCL's CE data path uses its
 * own per-process cudaMalloc FIFO — it never needs the cross-process dptr.
 */

#define _GNU_SOURCE
#include <dlfcn.h>

typedef int cudaError_t;
#define CUDA_HOST_REGISTER_MAPPED 0x04u

static cudaError_t (*real_fn)(void*, __SIZE_TYPE__, unsigned int);

cudaError_t cudaHostRegister(void *ptr, __SIZE_TYPE__ size, unsigned int flags) {
    if (!real_fn)
        real_fn = (cudaError_t (*)(void*, __SIZE_TYPE__, unsigned int))
                  dlsym(RTLD_NEXT, "cudaHostRegister");
    flags &= ~CUDA_HOST_REGISTER_MAPPED;
    return real_fn(ptr, size, flags);
}
