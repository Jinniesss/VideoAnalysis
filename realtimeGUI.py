import sys
import random
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import *
from PyQt6.QtMultimediaWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = ''
        self.setWindowTitle("Video Player")
        # self.setGeometry(100, 100, 1024, 768)

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.video_widget.setFixedSize(800, 600)

        self.select_video_button = QPushButton("Select Video")
        self.select_video_button.setFixedSize(100, 30)
        self.select_video_button.clicked.connect(self.select_video)

        self.label_fname = ''
        self.select_label_button = QPushButton("Select Labels")
        self.select_label_button.setFixedSize(100, 30)

        # 'nest' is actually behavioural state
        self.nest = QLabel()
        self.nest.setText("NONE")
        self.nest.setFixedSize(80, 30)
        self.nest.setStyleSheet("background-color: gray;border: 1px solid black;")
        self.nest.setFont(QFont('Arial',20))
        self.nest.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 'nest1' is actually nest state
        self.nest1 = QLabel()
        self.nest1.setText("XXX")
        self.nest1.setFixedSize(60, 30)
        self.nest1.setStyleSheet("background-color: gray;border: 1px solid black;")
        self.nest1.setFont(QFont('Arial', 20))
        self.nest1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 'nest2' is actually sleep state
        self.nest2 = QLabel()
        self.nest2.setText("XXX")
        self.nest2.setFixedSize(85, 30)
        self.nest2.setStyleSheet("background-color: gray;border: 1px solid black;")
        self.nest2.setFont(QFont('Arial', 20))
        self.nest2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start▶️")
        self.start_button.clicked.connect(self.start_video)

        self.pause_button = QPushButton("Pause⏸")
        self.pause_button.clicked.connect(self.pause_video)

        self.stop_button = QPushButton("Stop⏹")
        self.stop_button.clicked.connect(self.stop_video)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # temporary -- testing file
        # vfname=r"G:\.shortcut-targets-by-id\16_yydX2VMUgk-VfcpJJ4IMz2ZCDKD6C-\Data_analysis\Mouse behavior\Videos\DLC_analysis\ASAP_video\M105\M105_S1\M105_S1.avi"
        # self.media_player.setSource(QUrl.fromLocalFile(vfname))
        # self.media_player.play()

        # layout setting
        layout_files = QHBoxLayout()
        layout_files.addWidget(self.select_video_button)
        layout_files.addWidget(self.select_label_button)
        layout_files.addWidget(self.nest)
        layout_files.addWidget(self.nest1)
        layout_files.addWidget(self.nest2)

        layout_playbuts = QHBoxLayout()
        layout_playbuts.addWidget(self.start_button)
        layout_playbuts.addWidget(self.pause_button)
        layout_playbuts.addWidget(self.stop_button)

        layout = QVBoxLayout()
        layout.addLayout(layout_files)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.time_label)
        layout.addLayout(layout_playbuts)
        layout.addWidget(self.slider)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_video(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        self.media_player.setSource(QUrl.fromLocalFile(fname))
        self.media_player.play()

    def start_video(self):
        self.media_player.play()

    def pause_video(self):
        self.media_player.pause()

    def stop_video(self):
        self.media_player.stop()

    def set_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        self.slider.setValue(position)
        self.update_time_label()

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        current_time = int(self.media_player.position() / 1000)  # Convert to seconds
        total_time = int(self.media_player.duration() / 1000)  # Convert to seconds
        current_time_str = QTime(0, 0).addSecs(current_time).toString(Qt.DateFormat.ISODate)
        total_time_str = QTime(0, 0).addSecs(total_time).toString(Qt.DateFormat.ISODate)
        self.time_label.setText(f"{current_time_str} / {total_time_str}")

    def update_nest(self,position):
        cur_frame = int(position/100)
        if len(self.df)==0:
            return
        if cur_frame>len(self.df):
            self.nest1.setText("ERROR")
            self.nest1.setFixedSize(80, 30)
            self.nest1.setStyleSheet("background-color: yellow;border: 1px solid black;")
            print(cur_frame,len(self.df))
            return
        if self.df['nest'][cur_frame] == 1:
            self.nest1.setText("IN")
            self.nest1.setFixedSize(80, 30)
            self.nest1.setStyleSheet("background-color: pink;border: 1px solid black;")
        elif self.df['nest'][cur_frame] == 0:
            self.nest1.setText("OUT")
            self.nest1.setFixedSize(80, 30)
            self.nest1.setStyleSheet("background-color: lightblue;border: 1px solid black;")
        else:
            self.nest1.setText("NaN")
            self.nest1.setFixedSize(80, 30)
            self.nest1.setStyleSheet("background-color: gray;border: 1px solid black;")

    def update_var(self,position):
        cur_frame = int(position/100)
        if len(self.df)==0:
            return
        if cur_frame>len(self.df):
            self.nest.setText("ERROR")
            self.nest.setFixedSize(80, 30)
            self.nest.setStyleSheet("background-color: yellow;border: 1px solid black;")
            print(cur_frame,len(self.df))
            return
        else:
            if self.df['movement_state'][cur_frame] == 1:
                self.nest.setText('immobility')
                self.nest.setFixedSize(150, 30)
                self.nest.setStyleSheet("background-color: yellow;border: 1px solid black;")
            elif np.isnan(self.df['movement_state'][cur_frame]):
                self.nest.setText('NaN')
                self.nest.setFixedSize(150, 30)
                self.nest.setStyleSheet("background-color: gray;border: 1px solid black;")
            elif self.df['movement_state'][cur_frame] == 2:
                self.nest.setText('locomotion')
                self.nest.setFixedSize(150, 30)
                self.nest.setStyleSheet("background-color: red;border: 1px solid black;")
            elif self.df['movement_state'][cur_frame] == 0:
                self.nest.setText('non-loco')
                self.nest.setFixedSize(150, 30)
                self.nest.setStyleSheet("background-color: lightgreen;border: 1px solid black;")
            else:
                self.nest.setText('...')
                self.nest.setFixedSize(150, 30)
                self.nest.setStyleSheet("background-color: gray;border: 1px solid black;")
            # self.nest.setText(str(self.df['centerbody3_var'][cur_frame])[:6])
            # self.nest.setFixedSize(150, 30)
            # self.nest.setStyleSheet("background-color: white;border: 1px solid black;")

    def update_sleep(self,position):
        cur_frame = int(position/100)
        if len(self.df)==0:
            return
        if cur_frame>len(self.df):
            self.nest2.setText("ERROR")
            # self.nest2.setFixedSize(80, 30)
            self.nest2.setStyleSheet("background-color: red;border: 1px solid black;")
            print(cur_frame,len(self.df))
            return
        if self.df['sleep_state'][cur_frame] == 1:
            self.nest2.setText("REM")
            # self.nest2.setFixedSize(60, 30)
            self.nest2.setStyleSheet("background-color: green;border: 1px solid black;")
        elif self.df['sleep_state'][cur_frame] == 2:
            self.nest2.setText("WAKE")
            # self.nest2.setFixedSize(80, 30)
            self.nest2.setStyleSheet("background-color: blue;border: 1px solid black;")
        elif self.df['sleep_state'][cur_frame] == 3:
            self.nest2.setText("NREM")
            # self.nest2.setFixedSize(80, 30)
            self.nest2.setStyleSheet("background-color: yellow;border: 1px solid black;")
        else:
            self.nest2.setText("NONE")
            # self.nest2.setFixedSize(80, 30)
            self.nest2.setStyleSheet("background-color: gray;border: 1px solid black;")

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure(figsize=(1, 1), dpi=100)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

        self.timespan = 10  # sec
        self.freq = 10  # frame/sec

        self.df = None

        self.axes.axvline(0, linestyle='--', color='red')  # Add dashed line
        self.axes.set_xlabel("time(sec)")
        self.axes.set_xlim(-self.timespan,self.timespan)

    def update_plot(self,position,data,name):
        self.axes.cla()
        cur_time = position/1000  # sec
        cur_frame = cur_time * self.freq
        time_step = 1/self.freq   # sec/frame
        max_time = len(data)/self.freq
        time_start = max(0, cur_time - self.timespan)
        time_end = min(cur_time + self.timespan + time_step, max_time)
        time = np.arange(time_start, time_end, time_step)

        # y = data[max(0,int(cur_frame-self.timespan*self.freq)):int(min(cur_frame+self.timespan*self.freq+1,len(data)))]
        data_start = int(time_start*self.freq)
        y = data[data_start:data_start+len(time)]

        self.axes.axvline(cur_time, linestyle='--', color='red')
        self.axes.set_xlim(cur_time-self.timespan, cur_time+self.timespan)
        self.axes.plot(time,y)
        self.axes.set_xlabel("time(sec)")
        self.axes.set_title(name)
        self.draw()

class Plot_Figures(QMainWindow):
    def __init__(self):
        super().__init__()
        size = QSize(200,100)
        self.p1 = MplCanvas()
        self.p1.setMinimumSize(size)
        self.p2 = MplCanvas()
        self.p2.setMinimumSize(size)
        self.p3 = MplCanvas()
        self.p3.setMinimumSize(size)
        self.p4 = MplCanvas()
        self.p4.setMinimumSize(size)
        self.p5 = MplCanvas()
        self.p5.setMinimumSize(size)
        self.p6 = MplCanvas()
        self.p6.setMinimumSize(size)

        self.Dataframe=''
        # time on each side of the mid-line
        #                   *to be modified as interface*

        # temporary -- testing file
        # lfname=r"G:\.shortcut-targets-by-id\16_yydX2VMUgk-VfcpJJ4IMz2ZCDKD6C-\Data_analysis\Mouse behavior\Videos\DLC_analysis\ASAP_video\M105\M105_S1\M105_S1_data.csv"
        # self.Dataframe = pd.read_csv(lfname)
        # self.update_plots(0)

        # layout setting
        fig_layout1 = QHBoxLayout()
        fig_layout1.addWidget(self.p1)
        fig_layout1.addWidget(self.p2)

        fig_layout2 = QHBoxLayout()
        fig_layout2.addWidget(self.p3)
        fig_layout2.addWidget(self.p4)

        fig_layout3 = QHBoxLayout()
        fig_layout3.addWidget(self.p5)
        fig_layout3.addWidget(self.p6)

        fig_layout = QVBoxLayout()
        fig_layout.addLayout(fig_layout1)
        fig_layout.addLayout(fig_layout2)
        fig_layout.addLayout(fig_layout3)

        container = QWidget()
        container.setLayout(fig_layout)
        self.setCentralWidget(container)

    def update_plots(self,position):
        return          # temporary
        if len(self.Dataframe) != 0:
            self.p1.update_plot(position,self.Dataframe['velocity'],'velocity')
            self.p2.update_plot(position,self.Dataframe['acceleration'],'acceleration')
            self.p3.update_plot(position,self.Dataframe['angle_left'],'angle_left')
            self.p4.update_plot(position, self.Dataframe['angle_right'], 'angle_right')
            self.p5.update_plot(position, self.Dataframe['angle_velocity'], 'angle_velocity')
            self.p6.update_plot(position, self.Dataframe['angle_acceleration'], 'angle_acceleration')

    def select_label(self):
        label_fname, _ = QFileDialog.getOpenFileName(self, 'Open file', "", "*.csv")
        label_fname = r'' + label_fname
        self.Dataframe = pd.read_csv(label_fname)
        # self.update_plots(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Behavior Analysis")

        self.video_player = VideoPlayer()
        self.figures = Plot_Figures()
        self.video_player.df = self.figures.Dataframe

        # select label file
        self.label_fname = ''
        self.video_player.select_label_button.clicked.connect(self.figures.select_label)
        self.video_player.select_label_button.clicked.connect(self.df_upd)

        # update the figures when video changes
        # self.video_player.media_player.positionChanged.connect(self.figures.update_plots)
        self.video_player.media_player.positionChanged.connect(self.video_player.update_nest)
        self.video_player.media_player.positionChanged.connect(self.video_player.update_var)
        self.video_player.media_player.positionChanged.connect(self.video_player.update_sleep)
        # set the layout
        layout = QHBoxLayout()

        layout.addWidget(self.video_player)
        # layout.addWidget(self.figures)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def df_upd(self):
        self.video_player.df = self.figures.Dataframe


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())