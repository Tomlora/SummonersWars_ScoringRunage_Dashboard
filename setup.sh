mkdir -p ~/.streamlit/
cat > ~/.streamlit/config.toml <<EOF
[server]
headless = true
port = $PORT
enableCORS = false

[theme]
base = "dark"
primaryColor = "#49A4FF"
backgroundColor = "#07111F"
secondaryBackgroundColor = "#101F33"
textColor = "#F4F7FB"
linkColor = "#69B5FF"
borderColor = "#263B55"
baseRadius = "medium"
buttonRadius = "medium"
font = "sans-serif"
EOF
