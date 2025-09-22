import os
import threading
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
from mutagen.mp3 import MP3
from pygame import mixer

class MelodyPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Melody Music Player")
        self.root.iconbitmap(r'images/melody.ico')
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        
        # Initialize mixer
        mixer.init()
        
        # Initialize variables
        self.paused = False
        self.muted = False
        self.playlist = []
        self.current_song_index = 0
        
        # Create status bar
        self.statusbar = ttk.Label(root, text="Welcome to Melody Music Player", relief=SUNKEN, anchor=W, font='Times 10 italic')
        self.statusbar.pack(side=BOTTOM, fill=X)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main frames
        self.create_frames()
        
        # Create playlist section
        self.create_playlist_section()
        
        # Create music controls
        self.create_music_controls()
        
        # Create volume controls
        self.create_volume_controls()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu_bar(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.about_us)
    
    def create_frames(self):
        # Left frame for playlist
        self.leftframe = Frame(self.root)
        self.leftframe.pack(side=LEFT, padx=30, pady=30)
        
        # Right frame for controls
        self.rightframe = Frame(self.root)
        self.rightframe.pack(side=RIGHT, pady=30, padx=30, fill=BOTH, expand=True)
        
        # Top frame for song details
        self.topframe = Frame(self.rightframe)
        self.topframe.pack(fill=X)
        
        # Middle frame for playback controls
        self.middleframe = Frame(self.rightframe)
        self.middleframe.pack(pady=30, padx=30)
        
        # Bottom frame for volume controls
        self.bottomframe = Frame(self.rightframe)
        self.bottomframe.pack()
    
    def create_playlist_section(self):
        # Playlist label
        playlist_label = ttk.Label(self.leftframe, text="Music Playlist", font='Helvetica 12 bold')
        playlist_label.pack(pady=5)
        
        # Playlist box
        self.playlistbox = Listbox(self.leftframe, width=40, height=15, selectbackground="#a6a6a6")
        self.playlistbox.pack(pady=5)
        self.playlistbox.bind('<Double-1>', lambda x: self.play_music())
        
        # Playlist buttons frame
        playlist_btn_frame = Frame(self.leftframe)
        playlist_btn_frame.pack(pady=5)
        
        # Add button
        addBtn = ttk.Button(playlist_btn_frame, text="+ Add", command=self.browse_file)
        addBtn.grid(row=0, column=0, padx=5)
        
        # Delete button
        delBtn = ttk.Button(playlist_btn_frame, text="- Delete", command=self.del_song)
        delBtn.grid(row=0, column=1, padx=5)
        
        # Clear all button
        clearBtn = ttk.Button(playlist_btn_frame, text="Clear All", command=self.clear_playlist)
        clearBtn.grid(row=0, column=2, padx=5)
    
    def create_music_controls(self):
        # Song info labels
        self.song_title_label = ttk.Label(self.topframe, text='Currently Playing: No song selected', font='Helvetica 12 bold')
        self.song_title_label.pack(pady=5)
        
        self.lengthlabel = ttk.Label(self.topframe, text='Total Length : --:--')
        self.lengthlabel.pack(pady=5)
        
        self.currenttimelabel = ttk.Label(self.topframe, text='Current Time : --:--', relief=GROOVE)
        self.currenttimelabel.pack(pady=5)
        
        # Load images for buttons
        self.playPhoto = PhotoImage(file='images/play.png')
        self.stopPhoto = PhotoImage(file='images/stop.png')
        self.pausePhoto = PhotoImage(file='images/pause.png')
        self.rewindPhoto = PhotoImage(file='images/rewind.png')
        self.mutePhoto = PhotoImage(file='images/mute.png')
        self.volumePhoto = PhotoImage(file='images/volume.png')
        
        # Play button
        self.playBtn = ttk.Button(self.middleframe, image=self.playPhoto, command=self.play_music)
        self.playBtn.grid(row=0, column=0, padx=10)
        
        # Stop button
        self.stopBtn = ttk.Button(self.middleframe, image=self.stopPhoto, command=self.stop_music)
        self.stopBtn.grid(row=0, column=1, padx=10)
        
        # Pause button
        self.pauseBtn = ttk.Button(self.middleframe, image=self.pausePhoto, command=self.pause_music)
        self.pauseBtn.grid(row=0, column=2, padx=10)
        
        # Previous and Next buttons
        self.prevBtn = ttk.Button(self.middleframe, text="⏮ Prev", command=self.prev_song)
        self.prevBtn.grid(row=1, column=0, padx=10, pady=10)
        
        self.nextBtn = ttk.Button(self.middleframe, text="Next ⏭", command=self.next_song)
        self.nextBtn.grid(row=1, column=2, padx=10, pady=10)
    
    def create_volume_controls(self):
        # Rewind button
        self.rewindBtn = ttk.Button(self.bottomframe, image=self.rewindPhoto, command=self.rewind_music)
        self.rewindBtn.grid(row=0, column=0, padx=10)
        
        # Volume button
        self.volumeBtn = ttk.Button(self.bottomframe, image=self.volumePhoto, command=self.mute_music)
        self.volumeBtn.grid(row=0, column=1, padx=10)
        
        # Volume scale
        self.scale = ttk.Scale(self.bottomframe, from_=0, to=100, orient=HORIZONTAL, command=self.set_vol)
        self.scale.set(70)  # Default volume
        mixer.music.set_volume(0.7)
        self.scale.grid(row=0, column=2, pady=15, padx=30)
    
    def browse_file(self):
        filename_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if filename_path:
            self.add_to_playlist(filename_path)
    
    def add_to_playlist(self, filename):
        if filename:
            filename_short = os.path.basename(filename)
            self.playlistbox.insert(END, filename_short)
            self.playlist.append(filename)
            self.statusbar['text'] = f"Added {filename_short} to playlist"
    
    def del_song(self):
        try:
            selected_song_index = self.playlistbox.curselection()[0]
            self.playlistbox.delete(selected_song_index)
            self.playlist.pop(selected_song_index)
            self.statusbar['text'] = "Song removed from playlist"
        except:
            tkinter.messagebox.showerror('Error', 'No song selected to delete')
    
    def clear_playlist(self):
        self.playlistbox.delete(0, END)
        self.playlist.clear()
        self.stop_music()
        self.statusbar['text'] = "Playlist cleared"
    
    def show_details(self, play_song):
        self.song_title_label['text'] = f"Currently Playing: {os.path.basename(play_song)}"
        
        file_data = os.path.splitext(play_song)
        
        if file_data[1] == '.mp3':
            audio = MP3(play_song)
            total_length = audio.info.length
        else:
            a = mixer.Sound(play_song)
            total_length = a.get_length()
        
        mins, secs = divmod(total_length, 60)
        mins = round(mins)
        secs = round(secs)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        self.lengthlabel['text'] = "Total Length - " + timeformat
        
        # Start thread to count time
        t1 = threading.Thread(target=self.start_count, args=(total_length,))
        t1.daemon = True
        t1.start()
    
    def start_count(self, t):
        current_time = 0
        while current_time <= t and mixer.music.get_busy():
            if self.paused:
                continue
            else:
                mins, secs = divmod(current_time, 60)
                mins = round(mins)
                secs = round(secs)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                self.currenttimelabel['text'] = "Current Time - " + timeformat
                time.sleep(1)
                current_time += 1
    
    def play_music(self):
        if self.paused:
            mixer.music.unpause()
            self.statusbar['text'] = "Music Resumed"
            self.paused = False
        else:
            try:
                self.stop_music()
                time.sleep(0.5)
                
                try:
                    selected_song_index = self.playlistbox.curselection()[0]
                    self.current_song_index = selected_song_index
                except:
                    # If no song is selected, play the first one
                    if self.playlist:
                        selected_song_index = 0
                        self.playlistbox.selection_set(0)
                        self.current_song_index = 0
                    else:
                        raise Exception("No songs in playlist")
                
                play_it = self.playlist[selected_song_index]
                mixer.music.load(play_it)
                mixer.music.play()
                self.statusbar['text'] = f"Playing - {os.path.basename(play_it)}"
                self.show_details(play_it)
            except Exception as e:
                tkinter.messagebox.showerror('Error', f"Cannot play music. {str(e)}")
    
    def stop_music(self):
        mixer.music.stop()
        self.currenttimelabel['text'] = "Current Time - 00:00"
        self.statusbar['text'] = "Music Stopped"
    
    def pause_music(self):
        self.paused = True
        mixer.music.pause()
        self.statusbar['text'] = "Music Paused"
    
    def rewind_music(self):
        self.play_music()
        self.statusbar['text'] = "Music Rewinded"
    
    def set_vol(self, val):
        volume = float(val) / 100
        mixer.music.set_volume(volume)
    
    def mute_music(self):
        if self.muted:
            mixer.music.set_volume(0.7)
            self.volumeBtn.configure(image=self.volumePhoto)
            self.scale.set(70)
            self.muted = False
            self.statusbar['text'] = "Volume Restored"
        else:
            mixer.music.set_volume(0)
            self.volumeBtn.configure(image=self.mutePhoto)
            self.scale.set(0)
            self.muted = True
            self.statusbar['text'] = "Music Muted"
    
    def next_song(self):
        try:
            if self.playlist:
                self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
                self.playlistbox.selection_clear(0, END)
                self.playlistbox.selection_set(self.current_song_index)
                self.playlistbox.activate(self.current_song_index)
                self.playlistbox.see(self.current_song_index)
                self.play_music()
        except:
            tkinter.messagebox.showerror('Error', 'No next song in playlist')
    
    def prev_song(self):
        try:
            if self.playlist:
                self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
                self.playlistbox.selection_clear(0, END)
                self.playlistbox.selection_set(self.current_song_index)
                self.playlistbox.activate(self.current_song_index)
                self.playlistbox.see(self.current_song_index)
                self.play_music()
        except:
            tkinter.messagebox.showerror('Error', 'No previous song in playlist')
    
    def about_us(self):
        tkinter.messagebox.showinfo('About Melody', 'Melody is a music player built using Python Tkinter and Pygame')
    
    def on_closing(self):
        self.stop_music()
        self.root.destroy()

# Main function
def main():
    root = tk.ThemedTk()
    root.get_themes()  # Get available themes
    root.set_theme("radiance")  # Set theme
    
    app = MelodyPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()