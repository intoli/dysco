" Source locally with vim-addon-local-vimrc
" https://github.com/MarcWeber/vim-addon-local-vimrc
augroup LOCAL_SETUP
  " Format Python files before saving them.
  autocmd BufWritePre *.py execute ':Isort'
  autocmd BufWritePre *.py execute ':Black'

  " Disable the line width so wrapping happens only on save.
  autocmd Filetype python setlocal textwidth=100 formatoptions-=t
augroup end
