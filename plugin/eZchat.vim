" =============================================================================
" File:        eZchat.vim
" Description: vim plugin to provide a solid eZchat client
" Maintainer:  Jean-Nicolas Lang
" License:     GPLv2+ -- look it up.
" Notes:       Much of this code is inspired by Gundo, but mostly rewritten in
"              Python.
" =============================================================================

"{{{ Init
if (exists('loaded_eZchat') || &cp)"{{{
    finish
endif
let loaded_eZchat = 1"}}}
"}}}

"{{{ Misc
command! -nargs=0 EZchatToggle call eZchat#eZToggle()
"}}}

function! EZResponseCll()
  silent call eZchat#eZResponseCll()
endfunction
