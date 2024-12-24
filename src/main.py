import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                           QMessageBox, QFormLayout, QGroupBox, QSpinBox, 
                           QScrollArea, QTabWidget, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDoubleValidator, QPainter, QColor, QImage, QPixmap
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import joblib
import os
from PyQt5 import QtWebEngineWidgets
import fitz

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.setMinimumSize(150, 150)
        self.setMaximumSize(150, 150)
        self.color = QColor(0, 123, 255)  # Default blue color

    def setProgress(self, value, color=None):
        self.progress = value
        if color:
            self.color = color
        self.update()

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        margin = 10
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background circle
        pen = painter.pen()
        pen.setWidth(10)
        pen.setColor(Qt.lightGray)
        painter.setPen(pen)
        painter.drawArc(margin, margin, width-2*margin, height-2*margin, 0, 360 * 16)
        
        # Draw progress
        pen.setColor(self.color)
        painter.setPen(pen)
        span = int(self.progress * 360 * 16 / 100)
        painter.drawArc(margin, margin, width-2*margin, height-2*margin, 90 * 16, -span)
        
        # Draw percentage text
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(margin, margin, width-2*margin, height-2*margin, 
                        Qt.AlignCenter, f"{self.progress:.1f}%")

class DataQualityTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_level = 1.0
        self.zoom_factor = 0.1
        self.current_page = 0
        self.doc = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Zoom controls
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(60)
        
        self.zoom_in_btn = QPushButton("Phóng to (+)")
        self.zoom_out_btn = QPushButton("Thu nhỏ (-)")
        self.reset_zoom_btn = QPushButton("Reset (100%)")
        
        button_style = """
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """
        
        for btn in [self.zoom_in_btn, self.zoom_out_btn, self.reset_zoom_btn]:
            btn.setStyleSheet(button_style)
        
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.reset_zoom_btn)
        controls_layout.addWidget(self.zoom_label)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Scroll area for PDF display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Label to display PDF pages
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.pdf_label)
        
        layout.addWidget(self.scroll_area)
        
        # Connect signals
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        # Load PDF
        self.load_pdf("File/Chat_luong_du_lieu.pdf")
        
    def load_pdf(self, path):
        if os.path.exists(path):
            self.doc = fitz.open(path)
            self.update_display()
    
    def update_display(self):
        if not self.doc:
            return
            
        # Get the current page
        page = self.doc[self.current_page]
        
        # Calculate zoom matrix
        zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
        
        # Get the pixmap
        pix = page.get_pixmap(matrix=zoom_matrix)
        
        # Convert to QImage
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        
        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(img)
        self.pdf_label.setPixmap(pixmap)
        
    def zoom_in(self):
        self.zoom_level = min(3.0, self.zoom_level + self.zoom_factor)
        self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
        self.update_display()
        
    def zoom_out(self):
        self.zoom_level = max(0.3, self.zoom_level - self.zoom_factor)
        self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
        self.update_display()
        
    def reset_zoom(self):
        self.zoom_level = 1.0
        self.zoom_label.setText("100%")
        self.update_display()
        
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y() / 120.0
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
            
    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoom_in()
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
            elif event.key() == Qt.Key_0:
                self.reset_zoom()
        super().keyPressEvent(event)

class AnalyticsDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget for different charts
        tab_widget = QTabWidget()
        
        # Tab 1: Overview
        overview_tab = QWidget()
        overview_layout = QHBoxLayout(overview_tab)
        
        # Progress indicators
        progress_group = QGroupBox("Tiến độ học tập")
        progress_layout = QVBoxLayout()
        
        # Progress bars
        self.credits_progress = CircularProgressBar()
        self.drl_progress = CircularProgressBar()
        self.dtb_progress = CircularProgressBar()
        
        # Labels for progress bars
        progress_layout.addWidget(QLabel("Tiến độ tín chỉ:"))
        progress_layout.addWidget(self.credits_progress)
        progress_layout.addWidget(QLabel("Điểm rèn luyện TB:"))
        progress_layout.addWidget(self.drl_progress)
        progress_layout.addWidget(QLabel("Điểm TB tích lũy:"))
        progress_layout.addWidget(self.dtb_progress)
        
        progress_group.setLayout(progress_layout)
        overview_layout.addWidget(progress_group)
# Results and warnings
        results_group = QGroupBox("Kết quả dự đoán")
        results_layout = QVBoxLayout()
        
        self.prediction_label = QLabel()
        self.prediction_label.setWordWrap(True)
        self.prediction_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("color: red; font-size: 12px;")
        
        self.recommendation_label = QLabel()
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet("color: blue; font-size: 12px;")
        
        results_layout.addWidget(self.prediction_label)
        results_layout.addWidget(self.warning_label)
        results_layout.addWidget(self.recommendation_label)
        results_group.setLayout(results_layout)
        overview_layout.addWidget(results_group)
        
        tab_widget.addTab(overview_tab, "Tổng quan")
        
        # Tab 2: Analysis Charts
        charts_tab = QWidget()
        charts_layout = QVBoxLayout(charts_tab)
        
        # Matplotlib figure
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        
        tab_widget.addTab(charts_tab, "Biểu đồ phân tích")
        
        # Tab 3: Data Quality
        data_quality_tab = DataQualityTab()
        tab_widget.addTab(data_quality_tab, "Chất lượng dữ liệu")
        
        layout.addWidget(tab_widget)

    def update_dashboard(self, data):
        """Update dashboard with new data"""
        # Update progress bars
        self.credits_progress.setProgress(
            data['credit_progress'], 
            QColor(0, 255, 0) if data['credit_progress'] >= 80 else QColor(255, 0, 0)
        )
        
        self.drl_progress.setProgress(
            data['avg_drl'], 
            QColor(0, 255, 0) if data['avg_drl'] >= 80 else QColor(255, 0, 0)
        )
        
        self.dtb_progress.setProgress(
            data['avg_dtb'] * 10,
            QColor(0, 255, 0) if data['avg_dtb'] >= 7 else QColor(255, 0, 0)
        )
        
        # Update prediction results
        if data['prediction'] == 1:
            self.prediction_label.setText("✅ Sinh viên có khả năng tốt nghiệp đúng hạn!")
            self.prediction_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
        else:
            self.prediction_label.setText("⚠️ Sinh viên có nguy cơ chậm tiến độ!")
            self.prediction_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")

        # Update warnings and recommendations
        warnings = []
        recommendations = []
        
        # Check disciplinary scores
        if data['avg_drl'] < 80:
            warnings.append("- Điểm rèn luyện trung bình thấp hơn 80")
            recommendations.append("- Tăng cường tham gia hoạt động đoàn thể và rèn luyện")
            
        # Check GPA
        if data['avg_dtb'] < 7:
            warnings.append("- Điểm trung bình tích lũy thấp hơn 7.0")
            recommendations.append("- Cải thiện kết quả học tập, đặc biệt các môn chuyên ngành")
            
        # Check credit progress
        expected_credits = (data['current_semester'] / 8) * data['sotc_daura']
        if data['sotc_tichluy'] < expected_credits:
            warnings.append(f"- Số tín chỉ tích lũy ({data['sotc_tichluy']}) thấp hơn kế hoạch ({int(expected_credits)})")
            recommendations.append("- Đăng ký thêm tín chỉ trong các kỳ tới để đảm bảo tiến độ")

        # Display warnings and recommendations
        if warnings:
            self.warning_label.setText("Các yếu tố rủi ro:\n" + "\n".join(warnings))
        else:
            self.warning_label.clear()
            
        if recommendations:
            self.recommendation_label.setText("Đề xuất cải thiện:\n" + "\n".join(recommendations))
        else:
            self.recommendation_label.setText("Tiếp tục duy trì kết quả học tập tốt!")

        # Draw analysis charts
        self.plot_analysis(data)

    def plot_analysis(self, data):
        """Draw analysis charts"""
        self.figure.clear()
        
        # Create 2x2 grid for charts
        gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        ax1 = self.figure.add_subplot(gs[0, 0])
        semesters = [i for i in range(1, data['current_semester'] + 1)]
        dtb_values = [data[f'dtb_hk{i}'] for i in semesters]
        
        ax1.plot(semesters, dtb_values, 'b-o', label='DTB')
        ax1.axhline(y=7, color='r', linestyle='--', label='Ngưỡng ĐTB = 7.0')
        ax1.set_title('Điểm trung bình các học kỳ')
        ax1.set_xlabel('Học kỳ')
        ax1.set_ylabel('Điểm trung bình')
        ax1.grid(True)
        ax1.legend()
        
        # 2. Line chart for disciplinary scores
        ax2 = self.figure.add_subplot(gs[0, 1])
        drl_values = [data[f'drl_hk{i}'] for i in semesters]
        
        ax2.plot(semesters, drl_values, 'g-o', label='ĐRL')
        ax2.axhline(y=80, color='r', linestyle='--', label='Ngưỡng ĐRL = 80')
        ax2.set_title('Điểm rèn luyện các học kỳ')
        ax2.set_xlabel('Học kỳ')
        ax2.set_ylabel('Điểm rèn luyện')
        ax2.grid(True)
        ax2.legend()
        
        # 3. Pie chart for credit progress
        ax3 = self.figure.add_subplot(gs[1, 0])
        credits_completed = abs(data['sotc_tichluy'])
        credits_remaining = max(0, data['sotc_daura'] - credits_completed)

        if credits_completed > 0 or credits_remaining > 0:
            ax3.pie([credits_completed, credits_remaining],
                labels=[f'Đã tích lũy\n({credits_completed} tín chỉ)',
                       f'Còn lại\n({credits_remaining} tín chỉ)'],
                colors=['#2ecc71', '#e74c3c'],
                autopct='%1.1f%%',
                startangle=90)
            ax3.set_title('Tiến độ tích lũy tín chỉ')
        else:
            ax3.text(0.5, 0.5, 'Không có dữ liệu',
                horizontalalignment='center',
                verticalalignment='center')
        
        # 4. Line chart for credits by semester
        ax4 = self.figure.add_subplot(gs[1, 1])
        sotc_values = [data[f'sotc_hk{i}'] for i in semesters]
        cumulative_sotc = np.cumsum(sotc_values)
        
        # Draw credits per semester
        ax4.bar(semesters, sotc_values, alpha=0.3, label='Số TC học kỳ')
        # Draw cumulative line
        ax4.plot(semesters, cumulative_sotc, 'r-o', label='TC tích lũy')
        
        # Calculate expected credits for each semester
        expected_credits = [(i/8) * data['sotc_daura'] for i in semesters]
        ax4.plot(semesters, expected_credits, 'g--', label='TC kỳ vọng')
        
        ax4.set_title('Tiến độ tích lũy tín chỉ theo kỳ')
        ax4.set_xlabel('Học kỳ')
        ax4.set_ylabel('Số tín chỉ')
        ax4.grid(True)
        ax4.legend()

        self.figure.tight_layout()
        self.canvas.draw()

class PredictionUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dự Đoán Kết Quả Học Tập')
        self.setGeometry(100, 100, 1200, 800)

        # Load model
        try:
            model_info = joblib.load("Model/Random_Forest.pkl")
            self.model = model_info['model']
            self.feature_columns = model_info['feature_columns']
            self.scaler = model_info['scaler']
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể load model: {str(e)}')
            sys.exit(1)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Input panel (left side)
        input_panel = QWidget()
        input_layout = QVBoxLayout(input_panel)

        # Scroll area for input form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QVBoxLayout(scroll_content)

        # General information
        info_group = QGroupBox("Thông tin chung")
        info_layout = QFormLayout()

        # Semester combo box
        self.semester_combo = QComboBox()
        self.semester_combo.addItems([f'Học kỳ {i}' for i in range(1, 11)])
        self.semester_combo.currentIndexChanged.connect(self.on_semester_changed)
        info_layout.addRow('Học kỳ hiện tại:', self.semester_combo)

        # Required credits
        self.required_credits = QLineEdit()
        self.required_credits.setValidator(QDoubleValidator(0, 200, 0))
        self.required_credits.setText('135')
        info_layout.addRow('Số tín chỉ đầu ra:', self.required_credits)

        # English certificate
        self.english_cert = QComboBox()
        self.english_cert.addItems(['Không', 'Có'])
        info_layout.addRow('Chứng chỉ tiếng Anh:', self.english_cert)

        info_group.setLayout(info_layout)
        self.form_layout.addWidget(info_group)

        # Dictionary to store input fields
        self.inputs = {
            'drl': {},  # Disciplinary scores
            'dtb': {},  # GPA
            'sotc': {}  # Credits
        }

        # Container for semester fields
        self.semester_container = QWidget()
        self.semester_layout = QVBoxLayout(self.semester_container)
        self.form_layout.addWidget(self.semester_container)

        # Summary group
        summary_group = QGroupBox("Tổng kết")
        summary_layout = QFormLayout()
# Labels for summary values
        self.avg_drl_label = QLabel('0.0')
        summary_layout.addRow('Điểm rèn luyện trung bình:', self.avg_drl_label)
        
        self.avg_dtb_label = QLabel('0.0')
        summary_layout.addRow('Điểm trung bình tích lũy:', self.avg_dtb_label)
        
        self.total_credits_label = QLabel('0')
        summary_layout.addRow('Tổng số tín chỉ tích lũy:', self.total_credits_label)
        
        summary_group.setLayout(summary_layout)
        self.form_layout.addWidget(summary_group)

        # Predict button
        predict_button = QPushButton('Dự đoán')
        predict_button.clicked.connect(self.predict)
        predict_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.form_layout.addWidget(predict_button)

        # Complete scroll area
        scroll.setWidget(scroll_content)
        input_layout.addWidget(scroll)
        main_layout.addWidget(input_panel, 1)

        # Dashboard panel (right side)
        self.dashboard = AnalyticsDashboard()
        main_layout.addWidget(self.dashboard, 2)

        # Initialize interface
        self.on_semester_changed()

    def create_semester_fields(self, semester_num):
        """Create input fields for a semester"""
        semester_group = QGroupBox(f'Học kỳ {semester_num}')
        form = QFormLayout()

        # Disciplinary score
        drl_input = QLineEdit()
        drl_input.setValidator(QDoubleValidator(0, 100, 2))
        drl_input.setPlaceholderText('0-100')
        drl_input.textChanged.connect(self.calculate_averages)
        self.inputs['drl'][semester_num] = drl_input
        form.addRow('Điểm rèn luyện:', drl_input)

        # GPA
        dtb_input = QLineEdit()
        dtb_input.setValidator(QDoubleValidator(0, 10, 2))
        dtb_input.setPlaceholderText('0-10')
        dtb_input.textChanged.connect(self.calculate_averages)
        self.inputs['dtb'][semester_num] = dtb_input
        form.addRow('Điểm trung bình:', dtb_input)

        # Credits
        sotc_input = QLineEdit()
        sotc_input.setValidator(QDoubleValidator(0, 30, 0))
        sotc_input.setPlaceholderText('0-30')
        sotc_input.textChanged.connect(self.calculate_totals)
        self.inputs['sotc'][semester_num] = sotc_input
        form.addRow('Số tín chỉ:', sotc_input)

        semester_group.setLayout(form)
        return semester_group

    def on_semester_changed(self):
        """Handle semester change"""
        # Clear all current widgets in semester container
        while self.semester_layout.count():
            item = self.semester_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create fields for selected semester
        current_semester = int(self.semester_combo.currentText().split()[-1])
        for i in range(1, current_semester + 1):
            self.semester_layout.addWidget(self.create_semester_fields(i))

    def calculate_averages(self):
        """Calculate averages"""
        try:
            current_semester = int(self.semester_combo.currentText().split()[-1])
            
            # Calculate average disciplinary score
            total_drl = 0
            count_drl = 0
            for i in range(1, current_semester + 1):
                if self.inputs['drl'][i].text():
                    drl = float(self.inputs['drl'][i].text() or 0)
                    if drl > 0:
                        total_drl += drl
                        count_drl += 1
            
            avg_drl = total_drl / max(count_drl, 1)
            self.avg_drl_label.setText(f'{avg_drl:.2f}')

            # Calculate cumulative GPA
            total_weighted_score = 0
            total_credits = 0
            for i in range(1, current_semester + 1):
                if self.inputs['dtb'][i].text() and self.inputs['sotc'][i].text():
                    dtb = float(self.inputs['dtb'][i].text() or 0)
                    credits = float(self.inputs['sotc'][i].text() or 0)
                    if dtb > 0 and credits > 0:
                        total_weighted_score += dtb * credits
                        total_credits += credits
            
            avg_dtb = total_weighted_score / max(total_credits, 1)
            self.avg_dtb_label.setText(f'{avg_dtb:.2f}')

        except Exception as e:
            print(f"Error calculating averages: {str(e)}")

    def calculate_totals(self):
        """Calculate total credits"""
        try:
            current_semester = int(self.semester_combo.currentText().split()[-1])
            total_credits = 0
            
            for i in range(1, current_semester + 1):
                if self.inputs['sotc'][i].text():
                    credits = float(self.inputs['sotc'][i].text() or 0)
                    total_credits += credits
            
            self.total_credits_label.setText(str(int(total_credits)))
        except Exception as e:
            print(f"Error calculating totals: {str(e)}")

    def validate_inputs(self):
        """Validate inputs"""
        try:
            current_semester = int(self.semester_combo.currentText().split()[-1])

            # Check required credits
            if not self.required_credits.text():
                raise ValueError('Vui lòng nhập số tín chỉ đầu ra')
            required_credits = float(self.required_credits.text())
            if required_credits <= 0:
                raise ValueError('Số tín chỉ đầu ra phải lớn hơn 0')

            # Calculate total accumulated credits
            total_credits = 0
            for i in range(1, current_semester + 1):
                if self.inputs['sotc'][i].text():
                    credits = float(self.inputs['sotc'][i].text())
                    total_credits += credits
                
            # Check if total credits exceeds required credits
            if total_credits > required_credits:
                raise ValueError(f'Tổng số tín chỉ tích lũy ({total_credits}) không thể vượt quá số tín chỉ đầu ra ({required_credits})')

            for i in range(1, current_semester + 1):
                # Check disciplinary score
                if not self.inputs['drl'][i].text():
                    raise ValueError(f'Vui lòng nhập điểm rèn luyện HK{i}')
                drl = float(self.inputs['drl'][i].text())
                if not 0 <= drl <= 100:
                    raise ValueError(f'Điểm rèn luyện HK{i} phải từ 0-100')

                # Check GPA
                if not self.inputs['dtb'][i].text():
                    raise ValueError(f'Vui lòng nhập điểm trung bình HK{i}')
                dtb = float(self.inputs['dtb'][i].text())
                if not 0 <= dtb <= 10:
                    raise ValueError(f'Điểm trung bình HK{i} phải từ 0-10')

                # Check credits
                if not self.inputs['sotc'][i].text():
                    raise ValueError(f'Vui lòng nhập số tín chỉ HK{i}')
                sotc = float(self.inputs['sotc'][i].text())
                if not 0 <= sotc <= 30:
                    raise ValueError(f'Số tín chỉ HK{i} phải từ 0-30')

            return True
        except ValueError as e:
            QMessageBox.warning(self, 'Lỗi nhập liệu', str(e))
            return False\
            
    def predict(self):
        """Perform prediction"""
        if not self.validate_inputs():
            return

        try:
            current_semester = int(self.semester_combo.currentText().split()[-1])
            
            # Collect data from input fields
            input_data = {}
            
            # Get semester data
            for i in range(1, 11):
                if i <= current_semester:
                    input_data[f'drl_hk{i}'] = float(self.inputs['drl'][i].text())
                    input_data[f'dtb_hk{i}'] = float(self.inputs['dtb'][i].text())
                    input_data[f'sotc_hk{i}'] = float(self.inputs['sotc'][i].text())
                else:
                    input_data[f'drl_hk{i}'] = 0
                    input_data[f'dtb_hk{i}'] = 0
                    input_data[f'sotc_hk{i}'] = 0

            # Add general information
            input_data.update({
                'sotc_tichluy': float(self.total_credits_label.text()),
                'sotc_daura': float(self.required_credits.text()),
                'hocky_thu': current_semester,
                'chungchi_av': 1 if self.english_cert.currentText() == 'Có' else 0
            })

            # Add calculated parameters
            input_data.update({
                'avg_drl': float(self.avg_drl_label.text()),
                'avg_dtb': float(self.avg_dtb_label.text()),
                'credit_progress': (input_data['sotc_tichluy'] / input_data['sotc_daura']) * 100,
                'current_semester': current_semester
            })

            # Prepare data for model
            predict_df = pd.DataFrame([input_data])
            predict_df = pd.get_dummies(predict_df)
            
            # Ensure all columns from training are present
            for col in self.feature_columns:
                if col not in predict_df.columns:
                    predict_df[col] = 0
            predict_df = predict_df.reindex(columns=self.feature_columns, fill_value=0)
            
            # Scale data
            predict_scaled = self.scaler.transform(predict_df)
            
            # Make prediction
            prediction = self.model.predict(predict_scaled)[0]
            probability = self.model.predict_proba(predict_scaled)[0]

            # Analyze influence factors
            risk_factors = []
            suggestions = []

            # 1. Check GPA
            if input_data['avg_dtb'] < 7.0:
                risk_factors.append({
                    'factor': 'Điểm trung bình tích lũy thấp',
                    'value': f"{input_data['avg_dtb']:.2f}",
                    'threshold': '7.0',
                    'impact': 'high'
                })
                suggestions.append("- Cần cải thiện điểm trung bình các môn học")

            # 2. Check disciplinary scores
            if input_data['avg_drl'] < 80:
                risk_factors.append({
                    'factor': 'Điểm rèn luyện trung bình thấp',
                    'value': f"{input_data['avg_drl']:.1f}",
                    'threshold': '80',
                    'impact': 'medium'
                })
                suggestions.append("- Tăng cường tham gia hoạt động đoàn thể và rèn luyện")

            # 3. Check credit progress
            expected_credits = (current_semester / 8) * input_data['sotc_daura']
            if input_data['sotc_tichluy'] < expected_credits:
                risk_factors.append({
                    'factor': 'Thiếu tín chỉ tích lũy',
                    'value': str(int(input_data['sotc_tichluy'])),
                    'threshold': str(int(expected_credits)),
                    'impact': 'high'
                })
                suggestions.append(f"- Cần đăng ký thêm tín chỉ (thiếu {int(expected_credits - input_data['sotc_tichluy'])} tín chỉ so với tiến độ)")

            # 4. Check English certificate
            if input_data['chungchi_av'] == 0 and current_semester >= 6:
                risk_factors.append({
                    'factor': 'Chưa có chứng chỉ tiếng Anh',
                    'value': 'Không',
                    'threshold': 'Cần có từ học kỳ 6',
                    'impact': 'high'
                })
                suggestions.append("- Cần hoàn thành chứng chỉ tiếng Anh")

            # Update dashboard with prediction results and analysis
            input_data.update({
                'prediction': prediction,
                'probability': probability[1] * 100,
                'risk_factors': risk_factors,
                'suggestions': suggestions
            })
            
            # Display results
            self.dashboard.update_dashboard(input_data)

        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Lỗi khi dự đoán: {str(e)}')

def main():
    # Set high DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    # Set application style
    style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 3px;
        }
        QComboBox {
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 3px;
        }
        QLabel {
            font-size: 12px;
        }
        QScrollArea {
            border: none;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            border: 1px solid #cccccc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: none;
        }
        QWebEngineView {
            background-color: #ffffff;
        }
        QPushButton {
            padding: 5px 10px;
            border-radius: 3px;
            background-color: #e0e0e0;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QScrollBar:vertical {
            border: none;
            background: #f0f0f0;
            width: 10px;
            margin: 0px;
        }
        QScrollBar:horizontal {
            border: none;
            background: #f0f0f0;
            height: 10px;
            margin: 0px;
        }
        QScrollBar::handle {
            background: #c0c0c0;
            border-radius: 5px;
        }
        QScrollBar::handle:hover {
            background: #a0a0a0;
        }
    """
    
    app.setStyleSheet(style)
    
    # Set environment variables for WebEngine
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-web-security --no-sandbox'
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'
    
    # Enable WebEngine settings
    QtWebEngineWidgets.QWebEngineProfile.defaultProfile().setHttpCacheType(
        QtWebEngineWidgets.QWebEngineProfile.NoCache)
    
    settings = QtWebEngineWidgets.QWebEngineSettings.globalSettings()
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PdfViewerEnabled, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.ScrollAnimatorEnabled, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.WebGLEnabled, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessFileUrls, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalStorageEnabled, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptEnabled, True)
    settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptCanOpenWindows, True)
    
    # Create and show main window
    window = PredictionUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()