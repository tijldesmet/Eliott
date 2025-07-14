from pathlib import Path
import PySimpleGUI as sg

from .core import process
from .utils import load_config, save_config


def main():
    sg.theme('DarkGrey13')
    layout = [
        [sg.Text('Source Folder'), sg.Input(key='SRC'), sg.FolderBrowse()],
        [sg.Text('Output Folder'), sg.Input(key='DST'), sg.FolderBrowse()],
        [sg.Button('Start'), sg.Button('Settings')],
        [sg.ProgressBar(max_value=1, orientation='h', size=(40, 20), key='PROG')],
        [sg.Text('', size=(60, 1), key='STATUS')],
    ]

    window = sg.Window('MP3 Organizer', layout, finalize=True)

    def show_settings():
        cfg = load_config()
        layout = [
            [sg.Text('SPOTIPY_CLIENT_ID'), sg.Input(cfg.get('SPOTIPY_CLIENT_ID', ''), key='CID')],
            [sg.Text('SPOTIPY_CLIENT_SECRET'), sg.Input(cfg.get('SPOTIPY_CLIENT_SECRET', ''), key='SECRET')],
            [sg.Text('SPOTIPY_REDIRECT_URI'), sg.Input(cfg.get('SPOTIPY_REDIRECT_URI', ''), key='REDIRECT')],
            [sg.Text('AUDD_API_KEY'), sg.Input(cfg.get('AUDD_API_KEY', ''), key='AUDD')],
            [sg.Button('Save'), sg.Button('Cancel')],
        ]
        win = sg.Window('Settings', layout, modal=True)
        while True:
            e, v = win.read()
            if e in (sg.WIN_CLOSED, 'Cancel'):
                break
            if e == 'Save':
                save_config({
                    'SPOTIPY_CLIENT_ID': v['CID'],
                    'SPOTIPY_CLIENT_SECRET': v['SECRET'],
                    'SPOTIPY_REDIRECT_URI': v['REDIRECT'],
                    'AUDD_API_KEY': v['AUDD'],
                })
                break
        win.close()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Start':
            src = Path(values['SRC'])
            dst = Path(values['DST'])
            process(src, dst, window)
        if event == 'Settings':
            show_settings()

    window.close()


if __name__ == '__main__':
    main()

