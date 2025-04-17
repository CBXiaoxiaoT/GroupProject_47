from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import datetime, timezone, timedelta
from TimeLocationUtils import get_location, get_utc_time  # 使用统一的数据获取方法
from matplotlib.colors import hex2color
from matplotlib.collections import LineCollection

class MapWidget(FigureCanvas):
    def __init__(self, parent=None):
        # 初始化位置信息属性（由 TimeLocationUtils 提供）
        self.current_lat = None
        self.current_lon = None
        # 控制是否显示位置标记，默认不显示（未解锁）
        self.show_location = False

        # 创建 Figure 并添加一个坐标轴，使用 PlateCarree 投影
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111, projection=ccrs.PlateCarree())
        super().__init__(self.fig)
        self.setParent(parent)

        # 设置背景为黑色
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')

        # 初始设置地图
        self.ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
        self.ax.coastlines(linewidth=1)
        self.ax.add_feature(cfeature.LAND, facecolor='#FFFFFF')
        self.ax.add_feature(cfeature.OCEAN, facecolor='#000000')

        self.draw_map()

    def draw_map(self):
        # 清除之前的绘图内容
        self.ax.clear()
        # 调整 Axes 在 Figure 中的位置（可选）
        self.ax.set_position([0.1, 0.3, 0.8, 0.6])

        self.ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
        self.ax.coastlines(linewidth=1)
        self.ax.add_feature(cfeature.LAND, facecolor='#C0C0C0')
        self.ax.add_feature(cfeature.OCEAN, facecolor='#000000')

        # 使用 TimeLocationUtils 获取当前 UTC 时间信息
        time_data = get_utc_time()
        decimal_utc = time_data["decimal_utc"]
        n = time_data["year_day"]

        # 计算太阳赤纬（弧度）
        decl = np.deg2rad(-23.44 * np.cos(2 * np.pi * (n + 10) / 365))

        # 构造经纬度网格
        lon = np.linspace(-180, 180, 361)
        lat = np.linspace(-90, 90, 181)
        lon2d, lat2d = np.meshgrid(lon, lat)

        # 纬度转弧度
        lat_rad = np.deg2rad(lat2d)

        # 计算日心时角（弧度）
        hour_angle_deg = (decimal_utc - 12) * 15 + lon2d
        hour_angle_rad = np.deg2rad(hour_angle_deg)

        # 计算太阳天顶角的余弦值
        cos_zenith = np.sin(lat_rad) * np.sin(decl) + np.cos(lat_rad) * np.cos(decl) * np.cos(hour_angle_rad)

        # 绘制晨昏线：余弦值为0时，表示太阳在地平线上
        cs_ori = self.ax.contour(
            lon, lat, cos_zenith,
            levels=[0],
            colors='#808080',
            linewidths=2,
            alpha=0,
            transform=ccrs.PlateCarree()
        )

        # 创建纬度掩膜（仅保留纬度 >=30 的区域）
        lat_mask = lat2d >= 30
        cos_zenith_masked = np.where(lat_mask, cos_zenith, np.nan)
        cs = self.ax.contour(
            lon, lat, cos_zenith_masked,
            levels=[0],
            colors='#808080',
            linewidths=2,
            transform=ccrs.PlateCarree()
        )

        # 获取所有等值线的路径数据
        paths = []
        for segs in cs_ori.allsegs:
            for seg in segs:
                paths.append(seg)

        base_color = np.array(hex2color('#808080'))

        # 对每条路径分别处理，绘制渐变透明效果
        for seg in paths:
            if seg.shape[0] < 2:
                continue
            segments = np.stack([seg[:-1], seg[1:]], axis=1)
            avg_lat = np.mean(segments[:, :, 1], axis=1)
            alphas = np.clip((avg_lat + 60) / 90, 0.1, 1)
            segment_colors = np.zeros((len(segments), 4))
            segment_colors[:, :3] = base_color
            segment_colors[:, 3] = alphas
            lc = LineCollection(
                segments,
                colors=segment_colors,
                linewidths=2,
                transform=ccrs.PlateCarree()
            )
            self.ax.add_collection(lc)

        # 对太阳高度角 < 0 的区域加深灰度
        self.ax.contourf(
            lon, lat, cos_zenith < 0,
            levels=[0.5, 1],
            colors=['#000000'],
            alpha=0.7,
            transform=ccrs.PlateCarree()
        )

        # 通过 TimeLocationUtils 获取当前位置
        loc = get_location()
        if loc:
            self.current_lat, self.current_lon = loc

        # 只有在解锁状态（show_location 为 True）时才绘制位置标记
        if self.show_location and self.current_lat and self.current_lon:
            self.ax.plot(
                self.current_lon, self.current_lat,
                marker='o',
                color='#F57200',
                markersize=10,
                markeredgecolor='#FFFFFF',
                markeredgewidth=2,
                transform=ccrs.PlateCarree()
            )

        # 刷新显示
        self.draw()

    def update_map(self):
        self.draw_map()
