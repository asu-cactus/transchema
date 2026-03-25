/*
 * nccl_shm_shim.c — LD_PRELOAD shim to strip cudaHostRegisterMapped from
 * cudaHostRegister calls made by NCCL's SHM transport setup.
 *
 * Background
 * ----------
 * NCCL's ncclShmOpen() calls:
 *   cudaHostRegister(hptr, size, cudaHostRegisterPortable | cudaHostRegisterMapped)
 *   cudaHostGetDevicePointer(&dptr, hptr, 0)
 *
 * With NCCL_SHM_USE_CUDA_MEMCPY=1 + NCCL_SHM_MEMCPY_MODE=3, the data path
 * uses CE (Copy Engine) and never touches the cross-process device pointer.
 * However, the cudaHostRegister call with cudaHostRegisterMapped still creates
 * a GPU mapping for the /dev/shm buffer.  When the *other* Apptainer worker
 * process (in a separate CUDA context) initialises its NCCL communicator, the
 * init kernels may attempt to access the registered device address obtained in
 * the *first* process's context → "CUDA error: an illegal memory access".
 *
 * Fix: intercept cudaHostRegister and strip cudaHostRegisterMapped (bit 2).
 * The registration still pins the memory (cudaHostRegisterPortable), but
 * cudaHostGetDevicePointer will return cudaErrorInvalidValue, so dptr stays
 * NULL.  NCCL's CE-mode path does not need dptr to be valid — it allocates
 * its own device FIFO via cudaMalloc inside the proxy thread.
 *
 * Build (inside the container or from the host if cross-compilation is
 * available — the container is x86_64 Linux):
 *   cc -O2 -shared -fPIC -o nccl_shm_shim.so nccl_shm_shim.c -ldl
 *
 * Usage:
 *   export LD_PRELOAD=/path/to/nccl_shm_shim.so
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>

/* cudaError_t is just an int; avoid pulling in CUDA headers */
typedef int cudaError_t;

/* cudaHostRegisterPortable = 0x02, cudaHostRegisterMapped = 0x04 */
#define CUDA_HOST_REGISTER_MAPPED 0x04

static cudaError_t (*real_cudaHostRegister)(void*, size_t, unsigned int) = 0;

cudaError_t cudaHostRegister(void *ptr, size_t size, unsigned int flags) {
    if (!real_cudaHostRegister) {
        real_cudaHostRegister = (cudaError_t (*)(void*, size_t, unsigned int))
            dlsym(RTLD_NEXT, "cudaHostRegister");
    }
    /* Strip the Mapped flag: the CE path doesn't need a GPU-visible pointer
     * for the /dev/shm buffer; removing Mapped prevents the cross-process
     * device-address fault in NCCL's SHM init kernels.                    */
    flags &= ~(unsigned int)CUDA_HOST_REGISTER_MAPPED;
    return real_cudaHostRegister(ptr, size, flags);
}
