#[allow(unused_imports)]
use tauri::{Manager, WebviewUrl, WebviewWindowBuilder};
use tauri_plugin_shell::{process::CommandEvent, ShellExt};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  let port = portpicker::pick_unused_port().expect("failed to find unused port");

  tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_shell::init())
    .plugin(tauri_plugin_localhost::Builder::new(port).build())
    .setup(move |app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      // ── Build the main window ──────────────────────────────────────
      // In dev mode Tauri already uses the Vite dev-server URL, so we
      // just create a normal app webview.  In release mode we point at
      // the localhost plugin so the page is served over plain HTTP,
      // which avoids mixed-content blocking when fetch() hits the
      // Python backend on http://127.0.0.1:39291.
      #[cfg(dev)]
      let url = WebviewUrl::App(std::path::PathBuf::from("/"));

      #[cfg(not(dev))]
      let url = {
        let url: tauri::Url = format!("http://localhost:{}", port)
          .parse()
          .unwrap();
        app.add_capability(
          tauri::ipc::CapabilityBuilder::new("localhost-capability")
            .remote(url.to_string())
            .window("main")
            .permission("core:default")
            .permission("dialog:default")
            .permission("shell:default"),
        )?;
        WebviewUrl::External(url)
      };

      WebviewWindowBuilder::new(app, "main", url)
        .title("ENVIX")
        .inner_size(1000.0, 800.0)
        .resizable(true)
        .fullscreen(false)
        .build()?;

      // ── Spawn the Python sidecar ───────────────────────────────────
      let sidecar_command = app.shell().sidecar("envix-backend")?;
      let (mut rx, child) = sidecar_command.spawn()?;

      tauri::async_runtime::spawn(async move {
        let _child = child;
        while let Some(event) = rx.recv().await {
          match event {
            CommandEvent::Stdout(line) => {
              log::info!("backend: {}", String::from_utf8_lossy(&line));
            }
            CommandEvent::Stderr(line) => {
              log::warn!("backend: {}", String::from_utf8_lossy(&line));
            }
            _ => {}
          }
        }
      });

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}

