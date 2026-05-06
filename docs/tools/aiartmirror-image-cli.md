# aiartmirror Image CLI

Repo-local Python wrapper for the OpenAI SDK against the aiartmirror OpenAI-compatible image endpoint.

## Dependencies

Install the minimum Python packages:

```powershell
py -3 -m pip install -r scripts/python/requirements-imagegen.txt
```

Or install them directly:

```powershell
py -3 -m pip install openai pillow numpy
```

## Environment

Set the API key in PowerShell:

```powershell
$env:AIARTMIRROR_API_KEY="your-token-here"
$env:AIARTMIRROR_IMAGE_MODEL="gpt-image-2"
$env:AIARTMIRROR_IMAGE_GROUP="gpt-image-2"
```

Persist it for future terminals:

```powershell
setx AIARTMIRROR_API_KEY "your-token-here"
setx AIARTMIRROR_IMAGE_MODEL "gpt-image-2"
setx AIARTMIRROR_IMAGE_GROUP "gpt-image-2"
```

Optional custom base URL:

```powershell
$env:AIARTMIRROR_BASE_URL="https://www.aiartmirror.com/v1"
```

Do not put the token into committed files.

## Direct usage

```powershell
py -3 scripts/python/aiartmirror_image_cli.py `
  --prompt "A retro JRPG hero sprite on a plain background" `
  --out output/imagegen/hero.png
```

URL return mode:

```powershell
py -3 scripts/python/aiartmirror_image_cli.py `
  --prompt "a serene mountain lake at dawn" `
  --response-format url `
  --out output/imagegen/lake.png
```

Prompt from file:

```powershell
py -3 scripts/python/aiartmirror_image_cli.py `
  --prompt-file tmp/imagegen/hero_prompt.txt `
  --out output/imagegen/hero.png `
  --manifest-out output/imagegen/hero.json
```

Dry run:

```powershell
py -3 scripts/python/aiartmirror_image_cli.py `
  --prompt "test" `
  --out output/imagegen/test.png `
  --dry-run
```

## Via dev CLI

```powershell
py -3 scripts/python/dev_cli.py generate-image `
  --prompt "A retro JRPG chest sprite on a plain background" `
  --out output/imagegen/chest.png
```

Provider-specific routing group:

```powershell
py -3 scripts/python/dev_cli.py generate-image `
  --model gpt-image-2 `
  --group gpt-image-2 `
  --prompt "来一张类似勇者斗恶龙主角在大地图上的像素风的图片，128*128" `
  --size auto `
  --quality auto `
  --out output/imagegen/dq-hero.png
```

## Notes

- Default model: `gpt-image-2`
- Default base URL: `https://www.aiartmirror.com/v1`
- Default API key env var: `AIARTMIRROR_API_KEY`
- Default model env var: `AIARTMIRROR_IMAGE_MODEL`
- Default group env var: `AIARTMIRROR_IMAGE_GROUP`
- If `gpt-image-2` returns `403`, check provider-side account or organization access first.
