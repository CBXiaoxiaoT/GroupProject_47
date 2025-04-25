from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import datetime, timezone, timedelta
from TimeLocationUtils import get_location, get_utc_time
from matplotlib.colors import hex2color
from matplotlib.collections import LineCollection

class MapWidget(FigureCanvas):
    def __init__(self, parent=None):
        # Initialize location attributes (provided by TimeLocationUtils)
        self.current_lat = None
        self.current_lon = None
        # Control whether to show location marker, default is False: locked
        self.show_location = False

        # Create Figure and add an Axes with PlateCarree projection
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111, projection=ccrs.PlateCarree())
        super().__init__(self.fig)
        self.setParent(parent)

        # Set black background
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')

        # Initial map setup
        self.ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
        self.ax.coastlines(linewidth=1)
        self.ax.add_feature(cfeature.LAND, facecolor='#FFFFFF')
        self.ax.add_feature(cfeature.OCEAN, facecolor='#000000')

        self.draw_map()

    def draw_map(self):
        # Clear previous drawings
        self.ax.clear()
        # Optionally adjust Axes position in Figure
        self.ax.set_position([0.1, 0.3, 0.8, 0.6])

        self.ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
        self.ax.coastlines(linewidth=1)
        self.ax.add_feature(cfeature.LAND, facecolor='#C0C0C0')
        self.ax.add_feature(cfeature.OCEAN, facecolor='#000000')

        # Get current UTC time information using TimeLocationUtils
        time_data = get_utc_time()
        decimal_utc = time_data["decimal_utc"]
        n = time_data["year_day"]

        # Calculate solar declination (radians)
        decl = np.deg2rad(-23.44 * np.cos(2 * np.pi * (n + 10) / 365))

        # Construct longitude-latitude grid
        lon = np.linspace(-180, 180, 361)
        lat = np.linspace(-90, 90, 181)
        lon2d, lat2d = np.meshgrid(lon, lat)

        # Convert latitude to radians
        lat_rad = np.deg2rad(lat2d)

        # Calculate solar hour angle (radians)
        hour_angle_deg = (decimal_utc - 12) * 15 + lon2d
        hour_angle_rad = np.deg2rad(hour_angle_deg)

        # Calculate cosine of solar zenith angle
        cos_zenith = np.sin(lat_rad) * np.sin(decl) + np.cos(lat_rad) * np.cos(decl) * np.cos(hour_angle_rad)

        # Plot terminator line: cos value 0 means sun at horizon
        cs_ori = self.ax.contour(
            lon, lat, cos_zenith,
            levels=[0],
            colors='#808080',
            linewidths=2,
            alpha=0,
            transform=ccrs.PlateCarree()
        )

        # Create latitude mask (retain only latitudes >=30)
        lat_mask = lat2d >= 30
        cos_zenith_masked = np.where(lat_mask, cos_zenith, np.nan)
        cs = self.ax.contour(
            lon, lat, cos_zenith_masked,
            levels=[0],
            colors='#808080',
            linewidths=2,
            transform=ccrs.PlateCarree()
        )

        # Extract all contour paths
        paths = []
        for segs in cs_ori.allsegs:
            for seg in segs:
                paths.append(seg)

        base_color = np.array(hex2color('#808080'))

        # Process each path separately for gradient transparency effect
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

        # Darken areas with negative solar altitude angle
        self.ax.contourf(
            lon, lat, cos_zenith < 0,
            levels=[0.5, 1],
            colors=['#000000'],
            alpha=0.7,
            transform=ccrs.PlateCarree()
        )

        # Get current location using TimeLocationUtils
        loc = get_location()
        if loc:
            self.current_lat, self.current_lon = loc

        # Draw location marker only if unlocked (show_location is True)
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

        # Refresh display
        self.draw()

    def update_map(self):
        self.draw_map()
