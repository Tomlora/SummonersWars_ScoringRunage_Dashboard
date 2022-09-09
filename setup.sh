mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
primaryColor = '#0083B9'\n\
backgroundColor = '#03152A'\n\
secondaryBackgroundColor = '#0083B9'\n\
textColor = '#FFFFFF'\n\
font = 'sans serif'\n\
" > ~/.streamlit/config.toml