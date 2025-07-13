from pathlib import Path
import PySimpleGUI as sg

from .core import process


def main():
    layout = [
        [sg.Text('Source Folder'), sg.Input(key='SRC'), sg.FolderBrowse()],
        [sg.Text('Output Folder'), sg.Input(key='DST'), sg.FolderBrowse()],
        [sg.Button('Start')],
        [sg.ProgressBar(max_value=1, orientation='h', size=(40, 20), key='PROG')],
        [sg.Text('', size=(60, 1), key='STATUS')],
    ]

    window = sg.Window('MP3 Organizer', layout, finalize=True, theme='DarkGrey13')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Start':
            src = Path(values['SRC'])
            dst = Path(values['DST'])
            process(src, dst, window)

    window.close()


if __name__ == '__main__':
    main()
