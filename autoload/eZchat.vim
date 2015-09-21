" =============================================================================
" File:        eZchat.vim
" Description: vim plugin to provide a solid eZchat client
" Maintainer:  Jean-Nicolas Lang
" License:     GPLv2+ -- look it up.
" Notes:       Much of this code is inspired by Gundo, but mostly rewritten in
"              Python.
" =============================================================================

"=============================================================================="
"                                     Init                                     "
"=============================================================================="

if v:version < '703'"{{{
    function! s:eZDidNotLoad()
        echohl WarningMsg
              \ |echomsg "eZchat could not get loaded: requires Vim 7.3+"
              \ |echohl None
    endfunction
    command! -nargs=0 eZToggle call s:eZidNotLoad()
    finish
endif"}}}

"=============================================================================="
"                              Global Attributes                               "
"=============================================================================="

if !exists('g:ez_width')"{{{
    let g:ez_width = 45
endif"}}}
if !exists('g:ez_preview_height')"{{{
    let g:ez_preview_height = 15
endif"}}}
if !exists('g:ez_preview_bottom')"{{{
    let g:ez_preview_bottom = 0
endif"}}}
if !exists('g:ez_statusline_height')"{{{
    let g:ez_statusline_height = 4
endif"}}}
if !exists('g:ez_map_move_older')"{{{
    let g:ez_map_move_older = 'j'
endif"}}}
if !exists('g:ez_map_move_newer')"{{{
    let g:ez_map_move_newer = 'k'
endif"}}}
if !exists('g:ez_map_close')"{{{
    let g:ez_map_close = 'q'
endif"}}}
if !exists('g:ez_prefer_python3')"{{{
    let g:ez_prefer_python3 = 0
endif"}}}
if !exists('g:ez_menu_right')"{{{
    let g:ez_menu_right = 0
endif"}}}
if !exists('g:ez_send_message')"{{{
    let g:ez_send_message = 'S'
endif"}}}
if !exists('g:ez_load_message')"{{{
    let g:ez_load_message = 'L'
endif"}}}

let s:has_supported_python = 0
if g:ez_prefer_python3 && has('python3')"{{{
    let s:has_supported_python = 2
    let g:_py=":py3 "
elseif has('python')"
    let s:has_supported_python = 1
    let g:_py=":py "
endif

if !s:has_supported_python
    function! s:eZDidNotLoad()
        echohl WarningMsg
              \ |echomsg "eZchat requires Vim to be compiled with Python 2.4+"
              \ |echohl None
    endfunction
    command! -nargs=0 eZToggle call s:eZDidNotLoad()
    finish
endif"}}}

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
"}}}

"=============================================================================="
"                             eZ Utility functions                             "
"=============================================================================="

function! s:eZGetTargetState()"{{{
    let target_line = getline(".")
    return matchstr(target_line, '[0-9]+')
endfunction"}}}

function! s:eZGoToWindowForBufferName(name)"{{{
    if bufwinnr(bufnr(a:name)) != -1
        exe bufwinnr(bufnr(a:name)) . "wincmd w"
        return 1
    else
        return 0
    endif
endfunction"}}}

function! s:eZIsVisible()"{{{
    if bufwinnr(bufnr("__ez_options__")) != -1
        return 1
    else
        return 0
    endif
endfunction"}}}

"=============================================================================="
"                          eZ Options buffer settings                          "
"=============================================================================="

function! s:eZMapKeys()"{{{
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_map_move_older . 
          \ " :call <sid>eZOptionMove(1)<CR>"
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_map_move_newer . 
          \ " :call <sid>eZOptionMove(-1)<CR>"
    nnoremap <script> <silent> <buffer> <CR> :call <sid>eZExecuteOption()<CR>
    nnoremap <script> <silent> <buffer> <down> :call <sid>eZOptionMove(1)<CR>
    nnoremap <script> <silent> <buffer> <up> :call <sid>eZOptionMove(-1)<CR>
    nnoremap <script> <silent> <buffer> gg gg:call <sid>eZOptionMove(1)<CR>
    nnoremap <script> <silent> <buffer> r :call <sid>eZRender()<CR>
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_map_close . 
          \ " :call <sid>eZClose()<CR>"
    cabbrev  <script> <silent> <buffer> quit call <sid>eZClose()
endfunction"}}}

function! s:eZOptionSettings()"{{{
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    setlocal nomodifiable
    setlocal filetype=ez
    setlocal nolist
    setlocal nonumber
    setlocal norelativenumber
    setlocal nowrap
    call s:eZSyntaxOptions()
    call s:eZMapKeys()
endfunction"}}}

function! s:eZSyntaxOptions()"{{{
    let b:current_syntax = 'ezoption'

    syn match eZCurrentLocation '-'
    syn match eZHelp '\v^".*$'
    syn match eZNumberField '\v\[[0-9]+\]'
    syn match eZNumber '\v[0-9]+' contained containedin=eZNumberField
    syn keyword online ON
    syn keyword offline OFF 
    hi kwRed  term=standout ctermfg=red guifg=Red
    hi kwGreen  term=standout ctermfg=green guifg=Green

    hi def link eZCurrentLocation Keyword
    hi def link eZHelp Comment
    hi def link eZNumberField Comment
    hi def link eZNumber Identifier
    hi def link online kwGreen
    hi def link offline kwRed
endfunction"}}}

"=============================================================================="
"                        eZ MessageBox buffer settings                         "
"=============================================================================="

function! s:MapMessageWriteKeys()"{{{
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_send_message .
          \ " :call <sid>eZSendMessage()<CR>"
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_load_message .
          \ " :call <sid>eZLoadMessages()<CR>"
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_map_close . 
          \ " :call <sid>eZMessageClose()<CR>"
endfunction"}}}

function! s:MapMessageBufferKeys()"{{{
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_map_close . 
          \ " :call <sid>eZMessageClose()<CR>"
endfunction"}}}

function! s:eZMapPreview()"{{{
    nnoremap <script> <silent> <buffer> q     :call <sid>eZClose()<CR>
    cabbrev  <script> <silent> <buffer> q     call <sid>eZClose()
    cabbrev  <script> <silent> <buffer> quit  call <sid>eZClose()
endfunction"}}}

function! s:eZOptionMessageBuffer()"{{{
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    setlocal nomodifiable
    setlocal filetype=ez_contacts
    setlocal nolist
    setlocal nonumber
    setlocal norelativenumber
    setlocal nowrap
    call s:eZSyntaxMessageBuffer()
    call s:MapMessageBufferKeys()
endfunction"}}}

function! s:eZSyntaxMessageBuffer()"{{{
    let b:current_syntax = 'ezmessagebox'

    syn match eZCurrentLocation '-'
    syn match eZHelp '\v^".*$'
    syn match eZNumberField '\v\[[0-9]+\]'
    syn match eZNumber '\v[0-9]+' contained containedin=eZNumberField

    hi def link eZCurrentLocation Keyword
    hi def link eZHelp Comment
    hi def link eZNumberField Comment
    hi def link eZNumber Identifier
endfunction"}}}

function! s:eZOptionMessageWrite()"{{{
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    setlocal nolist
    setlocal nonumber
    setlocal norelativenumber
    setlocal nowrap
    call s:MapMessageWriteKeys()
endfunction"}}}

function! s:eZStatusLineBuffer()"{{{
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    setlocal nomodifiable
    setlocal nolist
    setlocal nonumber
    setlocal norelativenumber
    setlocal nowrap
    call s:StatusLineBufferKeys()
endfunction"}}}

"=============================================================================="
"                                eZ StatusLine                                 "
"=============================================================================="

function! s:StatusLineBufferKeys()"{{{
    exec 'nnoremap <script> <silent> <buffer> ' . g:ez_map_close . 
          \ " :call <sid>eZStatusLineClose()<CR>"
endfunction"}}}

"=============================================================================="
"                     eZ Options buffer/window management                      "
"=============================================================================="

function! s:eZResizeBuffers(backto)"{{{
    call s:eZGoToWindowForBufferName('__ez_options__')
    exe "vertical resize " . g:ez_width
    exe a:backto . "wincmd w"
endfunction"}}}

function! s:eZOpenOptions()"{{{
    let existing_preview_buffer = bufnr("__ez_options__")

    if existing_preview_buffer == -1
        if g:ez_preview_bottom
            exe "botright new __ez_options__"
          else
            if g:ez_menu_right
                exe "botright vnew __ez_options__"
            else
                exe "topleft vnew __ez_options__"
            endif
        endif

        call s:eZResizeBuffers(winnr())
    else
        let existing_preview_window = bufwinnr(existing_preview_buffer)

        if existing_preview_window != -1
            if winnr() != existing_preview_window
                exe existing_preview_window . "wincmd w"
            endif
        else
            if g:ez_preview_bottom
                exe "botright split +buffer" . existing_preview_buffer
            else
                if g:ez_menu_right
                    exe "botright vsplit +buffer" . existing_preview_buffer
                else
                    exe "topleft vsplit +buffer" . existing_preview_buffer
                endif
            endif
        call s:eZResizeBuffers(winnr())
        endif
    endif
    if exists("g:ez_preview_statusline")
        let &l:statusline = g:ez_preview_statusline
    endif
endfunction"}}}

function! s:eZOpen()"{{{
    " Source python modules
    if !exists('g:ez_py_loaded')
        if s:has_supported_python == 2 && g:ez_prefer_python3
            exe 'py3file ' . s:plugin_path . '/optionmenu.py'
            exe 'py3file ' . s:plugin_path . '/relay.py'
            exe 'py3file ' . s:plugin_path . '/messagebox.py'
            exe 'py3file ' . s:plugin_path . '/statusline.py'
            exe 'py3file ' . s:plugin_path . '/processbox.py'
            python3 initPythonModule()
        else
            exe 'pyfile ' . s:plugin_path . '/optionmenu.py'
            exe 'pyfile ' . s:plugin_path . '/relay.py'
            exe 'pyfile ' . s:plugin_path . '/messagebox.py'
            exe 'pyfile ' . s:plugin_path . '/statusline.py'
            exe 'pyfile ' . s:plugin_path . '/processbox.py'
            python initPythonModule()
        endif

        if !s:has_supported_python
            function! s:eZDidNotLoad()
                echohl WarningMsg|echomsg "eZchat unavailable: requires Vim 7.3+"|echohl None
            endfunction
            command! -nargs=0 eZToggle call s:eZDidNotLoad()
            call s:eZDidNotLoad()
            return
        endif"

        let g:ez_py_loaded = 1
    endif

    " Save `splitbelow` value and set it to default to avoid problems with
    " positioning new windows.
    let saved_splitbelow = &splitbelow
    let &splitbelow = 0

    call s:eZOpenOptions()
    exe bufwinnr(g:ez_target_n) . "wincmd w"

    call s:eZRender()

    " Restore `splitbelow` value.
    let &splitbelow = saved_splitbelow
endfunction"}}}

function! s:eZToggle()"{{{
    if s:eZIsVisible()
        call s:eZClose()
    else
        let g:ez_target_n = bufnr('')
        let g:ez_target_f = @%
        call s:eZOpen()
    endif
endfunction"}}}

function! s:eZClose()"{{{
    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 eZMenu.menu_move_up()
    else
        python eZMenu.menu_move_up()
    endif
endfunction"}}}

"=============================================================================="
"                             eZ Options Commands                              "
"=============================================================================="

function! s:eZExecuteOption()"{{{
    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 eZExecuteOption()
    else
        python eZExecuteOption()
    endif
endfunction"}}}

function! s:eZOptionMove(direction) "{{{

    let b:direction = a:direction
    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 eZMenu.move_cursor()
    else
        python eZMenu.move_cursor()
    endif

endfunction"}}}

"=============================================================================="
"                            eZ MessageBox Commands                            "
"=============================================================================="

function! s:eZMessageClose()"{{{
    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 MessageBox.close_message_box()
    else
        python MessageBox.close_message_box()
    endif
endfunction"}}}

function! s:eZSendMessage() "{{{

    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 MessageBox.send_message()
    else
        python MessageBox.send_message()
    endif

endfunction"}}}

function! s:eZLoadMessages() "{{{

    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 MessageBox.load_messages()
    else
        python MessageBox.load_messages()
    endif

endfunction"}}}

"=============================================================================="
"                            eZ Statusline Commands                            "
"=============================================================================="

function! s:eZStatusLineClose()"{{{
    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 StatusLine.close()
    else
        python StatusLine.close()
    endif
endfunction"}}}

"=============================================================================="
"                                  eZ Render                                   "
"=============================================================================="

function! s:eZRender()"{{{
    if s:has_supported_python == 2 && g:ez_prefer_python3
        python3 eZRender()
    else
        python eZRender()
    endif
endfunction"}}}

function! g:eZResponseCll()"{{{
  if s:has_supported_python == 2 && g:ez_prefer_python3
    python3 eZResponse()
  else
    python eZResponse()
  endif
endfunction"}}}

"=============================================================================="
"                                 eZ Shutdown                                  "
"=============================================================================="

function! s:eZShutdown()"{{{
  if s:has_supported_python == 2 && g:ez_prefer_python3
    python3 eZShutdown()
  else
    python eZShutdown()
  endif
endfunction"}}}

"=============================================================================="
"                                 Global Calls                                 "
"=============================================================================="
 
function! eZchat#eZToggle()"{{{
    call s:eZToggle()
    "call g:eZResponseCll()
endfunction"}}}

function! eZchat#eZResponseCll()"{{{
    call g:eZResponseCll()
endfunction"}}}

augroup eZAug
    autocmd!
    autocmd BufNewFile __ez_options__ call s:eZOptionSettings()
    autocmd BufNewFile __ez_message_buffer__ call s:eZOptionMessageBuffer()
    autocmd BufNewFile __ez_write_buffer__ call s:eZOptionMessageWrite()
    autocmd BufNewFile __ez_statusline_buffer__ call s:eZStatusLineBuffer()
    autocmd VimLeavePre * call s:eZShutdown()
augroup END
