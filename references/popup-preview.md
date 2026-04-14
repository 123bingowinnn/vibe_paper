# Popup Preview

Vibe Paper exposes the native preview window through a script entrypoint so agents do not need to reason about the desktop UI itself.

Use:

```powershell
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\scripts\open-preview.ps1 -ProjectRoot <PROJECT_ROOT> -Lang zh
```

The popup preview opens the native PyQt window, renders `paper/build/main_preview.pdf`, and keeps the interface preview-first. Source, file tree, and build log remain optional panels.

For project initialization or environment checks, use the companion scripts:

```powershell
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\scripts\init-workspace.ps1 ...
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\scripts\check-env.ps1
```

For direct desktop launching without the skill-facing alias, the legacy runtime entrypoint remains `tools/start-vibe-paper.ps1`.
