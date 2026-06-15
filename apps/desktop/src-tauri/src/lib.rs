#[tauri::command]
fn read_text_file(path: String) -> Result<String, String> {
    // Reads a file the user explicitly selected via the native dialog. Doing the read in
    // Rust avoids the fs-plugin path-scope ACL, which would otherwise reject arbitrary
    // user-picked locations.
    std::fs::read_to_string(&path).map_err(|error| error.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![read_text_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
