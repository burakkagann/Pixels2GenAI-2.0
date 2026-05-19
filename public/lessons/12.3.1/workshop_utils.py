import sys

try:
    import torch
except ImportError:
    print("Error: PyTorch not installed.")
    print("Install with: pip install -r requirements_workshop_cpu.txt")
    print("         or: pip install -r requirements_workshop_gpu.txt")
    sys.exit(1)

def get_device_with_confirmation(task_type="generation"):
    """
    Detect hardware and confirm with user before proceeding.

    Checks for accelerators in order: CUDA (NVIDIA) > MPS (Apple Silicon) > CPU

    Parameters:
        task_type: Description of the task ("generation", "exploration", "training")

    Returns:
        tuple: (device string ('cuda', 'mps', or 'cpu'), recommended sample count)
    """
    cuda_available = torch.cuda.is_available()
    mps_available = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()

    # Check for CUDA (NVIDIA GPU)
    if cuda_available:
        try:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        except Exception:
            gpu_name = "Unknown GPU"
            gpu_memory = 0

        print()
        print("=" * 60)
        print("NVIDIA GPU DETECTED")
        print("=" * 60)
        print(f"  Device: {gpu_name}")
        print(f"  Memory: {gpu_memory:.1f} GB")
        print()

        if task_type == "generation":
            print("  Estimated time: ~30 seconds for 16 samples")
            print("  Sample count: 16")
        elif task_type == "exploration":
            print("  Estimated time: ~2-3 minutes total")
        elif task_type == "training":
            print("  Estimated time: 4-6 hours")
            print("  Batch size: 32")

        print("=" * 60)
        print()

        response = input("Proceed with CUDA GPU? [Y/n]: ").strip().lower()

        if response in ['', 'y', 'yes']:
            print("Using CUDA GPU...")
            return 'cuda', 16
        else:
            print("Switching to CPU mode...")
            return 'cpu', 4

    # Check for MPS (Apple Silicon)
    elif mps_available:
        print()
        print("=" * 60)
        print("APPLE SILICON (MPS) DETECTED")
        print("=" * 60)
        print(f"  Device: Apple Silicon GPU")
        print(f"  Backend: Metal Performance Shaders")
        print()

        if task_type == "generation":
            print("  Estimated time: ~1-2 minutes for 16 samples")
            print("  Sample count: 16")
        elif task_type == "exploration":
            print("  Estimated time: ~3-5 minutes total")
        elif task_type == "training":
            print("  Estimated time: 6-10 hours")
            print("  Batch size: 16")
            print()
            print("  NOTE: MPS training is slower than NVIDIA CUDA.")

        print("=" * 60)
        print()

        response = input("Proceed with MPS (Apple Silicon)? [Y/n]: ").strip().lower()

        if response in ['', 'y', 'yes']:
            print("Using Apple Silicon MPS...")
            return 'mps', 16
        else:
            print("Switching to CPU mode...")
            return 'cpu', 4

    # Fallback to CPU
    else:
        print()
        print("=" * 60)
        print("NO GPU DETECTED - Running in CPU mode")
        print("=" * 60)
        print()

        if task_type == "generation":
            print("  Estimated time: ~2-5 minutes for 4 samples")
            print("  Sample count: 4 (reduced for faster completion)")
        elif task_type == "exploration":
            print("  Estimated time: ~10-20 minutes total")
        elif task_type == "training":
            print("  Estimated time: 24-48 hours")
            print("  Batch size: 8")
            print()
            print("  NOTE: Training on CPU is very slow.")
            print("  Consider downloading pre-trained weights instead.")

        print("=" * 60)
        print()

        response = input("Proceed with CPU? [Y/n]: ").strip().lower()

        if response in ['', 'y', 'yes']:
            print("Using CPU...")
            return 'cpu', 4
        else:
            print("Cancelled by user.")
            sys.exit(0)

def get_training_params(device):
    """
    Return device-appropriate training parameters.

    Parameters:
        device: 'cuda', 'mps', or 'cpu'

    Returns:
        dict with batch_size, gradient_accumulate, amp, estimated_time
    """
    if device == 'cuda':
        return {
            'batch_size': 32,
            'gradient_accumulate': 2,
            'amp': True,
            'estimated_time': '4-6 hours'
        }
    elif device == 'mps':
        return {
            'batch_size': 16,
            'gradient_accumulate': 4,
            'amp': False,  # AMP not fully supported on MPS yet
            'estimated_time': '6-10 hours'
        }
    else:
        return {
            'batch_size': 8,
            'gradient_accumulate': 4,
            'amp': False,  # AMP not effective on CPU
            'estimated_time': '24-48 hours'
        }

def confirm_cpu_training(params):
    """
    Show strong warning and require explicit confirmation for CPU training.

    Parameters:
        params: Training parameters dict from get_training_params()

    Returns:
        bool: True if user confirms, exits program if not
    """
    print()
    print("!" * 60)
    print("! WARNING: TRAINING ON CPU")
    print("!" * 60)
    print(f"!")
    print(f"!  Estimated time: {params['estimated_time']}")
    print(f"!  Batch size: {params['batch_size']}")
    print(f"!")
    print("!  RECOMMENDATION: Download pre-trained weights instead.")
    print("!  This will save you 24-48 hours of waiting.")
    print("!")
    print("!  Pre-trained weights download:")
    print("!  https://github.com/burakkagann/Pixels2GenAI/releases")
    print("!")
    print("!" * 60)
    print()

    confirm = input("Type 'yes' to continue training on CPU: ").strip().lower()

    if confirm != 'yes':
        print()
        print("Training cancelled.")
        print("Download pre-trained weights from:")
        print("https://github.com/burakkagann/Pixels2GenAI/releases/tag/v1.0.0-ddpm-weights")
        sys.exit(0)

    return True

def get_device_info():
    """
    Get device information without user interaction.

    Returns:
        dict with device details including CUDA, MPS, and CPU info
    """
    cuda_available = torch.cuda.is_available()
    mps_available = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()

    # Determine best device
    if cuda_available:
        device = 'cuda'
    elif mps_available:
        device = 'mps'
    else:
        device = 'cpu'

    info = {
        'cuda_available': cuda_available,
        'mps_available': mps_available,
        'device': device,
        'torch_version': torch.__version__,
    }

    if cuda_available:
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['gpu_count'] = torch.cuda.device_count()
        info['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    elif mps_available:
        info['gpu_name'] = 'Apple Silicon (MPS)'
        info['gpu_count'] = 1
        info['gpu_memory_gb'] = 0  # MPS doesn't report memory
    else:
        info['gpu_name'] = None
        info['gpu_count'] = 0
        info['gpu_memory_gb'] = 0

    return info

# =============================================================================
# Quick test when run directly
# =============================================================================

if __name__ == '__main__':
    print("Workshop Utils - Device Detection Test")
    print("=" * 40)

    info = get_device_info()
    print(f"PyTorch version: {info['torch_version']}")
    print(f"CUDA available: {info['cuda_available']}")
    print(f"MPS available:  {info['mps_available']}")
    print(f"Best device:    {info['device']}")

    if info['cuda_available']:
        print(f"GPU: {info['gpu_name']}")
        print(f"GPU Memory: {info['gpu_memory_gb']:.1f} GB")
    elif info['mps_available']:
        print(f"GPU: {info['gpu_name']}")

    print()
    print("Testing user confirmation flow...")
    device, samples = get_device_with_confirmation("generation")
    print(f"Selected device: {device}")
    print(f"Sample count: {samples}")
