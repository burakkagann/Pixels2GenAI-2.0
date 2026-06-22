#requires -Version 5.1
# Publishes Module 12 trained-checkpoint releases to burakkagann/Pixels2GenAI-2.0.
# One-shot migration script - not part of the daily workflow.
# Run from any directory; paths are absolute.

$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
$ErrorActionPreference = "Continue"

$repo   = "burakkagann/Pixels2GenAI-2.0"
$target = "main"
$v1     = "C:\Users\User\Desktop\git-repos\numpy-to-genAI\content\Module_12_generative_ai_models"

function Publish-Release {
    param(
        [Parameter(Mandatory)][string]$Tag,
        [Parameter(Mandatory)][string]$Title,
        [Parameter(Mandatory)][string]$Notes,
        [Parameter(Mandatory)][string[]]$Files
    )
    Write-Host ""
    Write-Host ("========== {0} ==========" -f $Tag)
    $missing = $false
    foreach ($f in $Files) {
        if (-not (Test-Path $f)) {
            Write-Host ("  MISSING: {0}" -f $f) -ForegroundColor Red
            $missing = $true
        } else {
            $sz = [math]::Round((Get-Item $f).Length / 1MB, 1)
            Write-Host ("  attach : {0}  ({1} MB)" -f (Split-Path $f -Leaf), $sz)
        }
    }
    if ($missing) { Write-Host "  SKIP (missing files)" -ForegroundColor Red; return }

    $null = & gh release view $Tag --repo $repo 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host ("  tag '{0}' already exists on {1} - uploading assets with --clobber" -f $Tag, $repo)
        & gh release upload $Tag @Files --repo $repo --clobber
    } else {
        Write-Host ("  creating release '{0}'" -f $Tag)
        & gh release create $Tag @Files --repo $repo --target $target --title $Title --notes $Notes
    }
    if ($LASTEXITCODE -eq 0) {
        Write-Host ("  OK: https://github.com/{0}/releases/tag/{1}" -f $repo, $Tag) -ForegroundColor Green
    } else {
        Write-Host ("  FAIL (gh exit {0})" -f $LASTEXITCODE) -ForegroundColor Red
    }
}

# --- ordered smallest first so failures surface fast ---

Publish-Release `
    -Tag   "v1.0.0-dreambooth-lora" `
    -Title "DreamBooth LoRA Weights - African Fabrics (Module 12.5.1)" `
    -Notes "Pre-trained LoRA adapter for Stable Diffusion v1.5, fine-tuned on the African Fabric dataset (Kaggle: mikuns/african-fabric). Used by lesson 12.5.1 DreamBooth Personalization to demonstrate parameter-efficient personalization without retraining the full model.`n`nAssets:`n- adapter_model.safetensors (~3 MB, LoRA weights)`n- adapter_config.json (PEFT config)`n`nLoad with the HuggingFace PEFT library; base model is runwayml/stable-diffusion-v1-5." `
    -Files @(
        (Join-Path $v1 "12.5_personalization_efficiency\12.5.1_dreambooth_personalization\models\fabric_lora\adapter_model.safetensors"),
        (Join-Path $v1 "12.5_personalization_efficiency\12.5.1_dreambooth_personalization\models\fabric_lora\adapter_config.json")
    )

Publish-Release `
    -Tag   "v1.0.0-vae-weights" `
    -Title "VAE Weights - African Fabrics (Module 12.2.2)" `
    -Notes "Pre-trained Variational Autoencoder weights for lesson 12.2.2 Interpolation Animations. Trained on the African Fabric dataset (Kaggle: mikuns/african-fabric) at 64x64 resolution.`n`nAssets:`n- vae_weights.pth (~27 MB)`n`nUsed to generate latent-space interpolation animations between two fabric patterns." `
    -Files @(
        (Join-Path $v1 "12.2_variational_autoencoders\12.2.2_interpolation_animations\vae_weights.pth")
    )

Publish-Release `
    -Tag   "v1.0.0-flow-matching-weights" `
    -Title "Flow Matching Weights - African Fabrics (Module 12.7.1)" `
    -Notes "Pre-trained Flow Matching model for lesson 12.7.1 Flow Matching. Trained on the African Fabric dataset (Kaggle: mikuns/african-fabric).`n`nAssets:`n- flow_matching_fabrics_latest.pt (~54 MB, latest training checkpoint)`n`nDemonstrates a continuous-time generative model that learns a velocity field mapping noise to data, an alternative to discrete-time diffusion." `
    -Files @(
        (Join-Path $v1 "12.7_modern_frontiers\12.7.1_flow_matching\models\flow_matching_fabrics_latest.pt")
    )

Publish-Release `
    -Tag   "stylegan-checkpoint" `
    -Title "StyleGAN2 Checkpoint - African Fabrics (Module 12.1.3)" `
    -Notes "Pre-trained StyleGAN2 checkpoint for lesson 12.1.3 StyleGAN Exploration. Trained on the African Fabric dataset (Kaggle: mikuns/african-fabric) at 64x64 resolution using lucidrains/stylegan2-pytorch.`n`nAssets:`n- model_99.pt (~189 MB, final checkpoint after 100 training rounds)`n`nUsed for latent-space interpolation, truncation comparisons, and style-mixing demonstrations." `
    -Files @(
        (Join-Path $v1 "12.1_generative_adversarial_networks\12.1.3_stylegan_exploration\models\african_fabrics\model_99.pt")
    )

Publish-Release `
    -Tag   "v1.0.0-pix2pix-weights" `
    -Title "Pix2Pix Weights - CMP Facades (Module 12.1.4)" `
    -Notes "Pre-trained Pix2Pix generator and discriminator for lesson 12.1.4 Pix2Pix Applications. Trained on the CMP Facades dataset (Kaggle: adlteam/facade-dataset) for label-to-photo translation of building facades.`n`nAssets:`n- generator_weights.pth (~208 MB, U-Net generator)`n- discriminator_weights.pth (~11 MB, PatchGAN discriminator)`n`nLearners can also retrain on the Anime Sketch Colorization dataset (Kaggle: ktaebum/anime-sketch-colorization-pair) for Exercise 3." `
    -Files @(
        (Join-Path $v1 "12.1_generative_adversarial_networks\12.1.4_pix2pix_applications\generator_weights.pth"),
        (Join-Path $v1 "12.1_generative_adversarial_networks\12.1.4_pix2pix_applications\discriminator_weights.pth")
    )

Publish-Release `
    -Tag   "v1.0.0-ddpm-weights" `
    -Title "DDPM Pre-trained Weights - African Fabrics (Module 12.3.1)" `
    -Notes "Pre-trained Denoising Diffusion Probabilistic Model for lesson 12.3.1 DDPM Basics. Trained for ~500,000 steps on the African Fabric dataset (Kaggle: mikuns/african-fabric) at 64x64 resolution.`n`nAssets:`n- ddpm_african_fabrics.pt (~545 MB, final model)`n`nFull training run takes ~15-20 hours on an RTX 5070Ti. Lessons use this pre-trained checkpoint by default; Exercise 3 documents the optional from-scratch retrain." `
    -Files @(
        (Join-Path $v1 "12.3_diffusion_models\12.3.1_ddpm_basics\models\ddpm_african_fabrics.pt")
    )

Publish-Release `
    -Tag   "v1.0.0-controlnet-weights" `
    -Title "ControlNet Weights - Fill50k + African Fabrics LoRA (Module 12.3.2)" `
    -Notes "Pre-trained ControlNet and companion LoRA for lesson 12.3.2 ControlNet Guided Generation.`n`nAssets:`n- controlnet_fill50k.pt (~1.38 GB) - ControlNet conditioned on the Fill50k dataset (HuggingFace: lllyasviel/ControlNet training data) for shape-guided generation`n- lora_african_fabrics.safetensors (~3 MB) - Style LoRA for African fabric patterns, combined with ControlNet for content+style control`n`nUpload may take several minutes for the 1.4 GB ControlNet checkpoint." `
    -Files @(
        (Join-Path $v1 "12.3_diffusion_models\12.3.2_controlnet_guided_generation\models\controlnet_fill50k.pt"),
        (Join-Path $v1 "12.3_diffusion_models\12.3.2_controlnet_guided_generation\models\lora_african_fabrics.safetensors")
    )

Write-Host ""
Write-Host "==========================================="
Write-Host "All releases processed. Final state:"
& gh release list --repo $repo
