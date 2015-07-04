# vim-eZchat
Vim plugin for eZchat

# shell setup
export ez_host='95.xxx.xxx.xxx'

export ez_port=64xxx

PYTHONPATH=$PYTHONPATH:~/eZchat/  <- your eZchat path

# Run
start vim with

vim --servername ez

if you want automatic event trigger


# default settings are set in autoload/eZchat.vim 
ez_width = 45

ez_preview_height = 15

ez_preview_bottom = 0

ez_statusline_height = 4

ez_map_move_older = 'j'

ez_map_move_newer = 'k'

ez_map_close = 'q'

ez_prefer_python3 = 0

ez_menu_right = 0

ez_send_message = 'S'


# Toggle eZchat

map <silent> <F4> :EZchatToggle<CR>
