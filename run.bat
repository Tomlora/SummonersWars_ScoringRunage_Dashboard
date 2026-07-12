@echo off

:: Création du dossier .streamlit
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"

:: Création du config.toml
(
echo [server]
echo headless = true
echo port = 8501
echo enableCORS = false
echo.
echo [theme]
echo primaryColor = '#0083B9'
echo backgroundColor = '#03152A'
echo secondaryBackgroundColor = '#0083B9'
echo textColor = '#FFFFFF'
echo font = 'sans serif'
) > "%USERPROFILE%\.streamlit\config.toml"

:: Activation du venv
call .venv\Scripts\activate

:: Lancement cloudflared
start cmd /k "C:\Users\Kevin\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe tunnel run scoringsw"

:: Lancement Streamlit
streamlit run scoring_runage.py --server.port 8501