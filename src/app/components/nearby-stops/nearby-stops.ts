import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NearbyStop } from '../../models/stop';
import { StopService } from '../../services/stop.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-nearby-stops',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './nearby-stops.html'
})
export class NearbyStops implements OnInit {
  stops: NearbyStop[] = [];
  loading: boolean = false;
  error: string | null = null;
  userLat: number | null = null;
  userLon: number | null = null;
  radius: number = 500;
  geolocationSupported: boolean = true;

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private stopService: StopService,
    private router: Router
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());
    this.checkGeolocationSupport();
    
    // Richiedi automaticamente la posizione al primo accesso
    if (this.geolocationSupported) {
      this.requestLocation();
    }
  }

  checkGeolocationSupport() {
    if (!navigator.geolocation) {
      this.geolocationSupported = false;
      this.error = 'nearby.geolocationNotSupported';
    }
  }

  requestLocation() {
    if (!navigator.geolocation) {
      this.error = 'nearby.geolocationNotSupported';
      return;
    }

    this.loading = true;
    this.error = null;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        this.userLat = position.coords.latitude;
        this.userLon = position.coords.longitude;
        this.loadNearbyStops();
      },
      (error) => {
        this.loading = false;
        switch (error.code) {
          case error.PERMISSION_DENIED:
            this.error = 'nearby.permissionDenied';
            break;
          case error.POSITION_UNAVAILABLE:
            this.error = 'nearby.positionUnavailable';
            break;
          case error.TIMEOUT:
            this.error = 'nearby.timeout';
            break;
          default:
            this.error = 'nearby.unknownError';
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }

  loadNearbyStops() {
    if (this.userLat === null || this.userLon === null) {
      return;
    }

    this.loading = true;
    this.error = null;

    this.stopService.getNearby(this.userLat, this.userLon, this.radius).subscribe({
      next: (response) => {
        this.stops = response.stops;
        this.loading = false;
        if (this.stops.length === 0) {
          this.error = 'nearby.noStopsFound';
        }
      },
      error: (err) => {
        console.error('Error loading nearby stops:', err);
        this.error = 'nearby.loadError';
        this.loading = false;
      }
    });
  }

  changeRadius(newRadius: number) {
    this.radius = newRadius;
    if (this.userLat !== null && this.userLon !== null) {
      this.loadNearbyStops();
    }
  }

  goToStop(stopId: string) {
    this.router.navigate(['/stop', stopId]);
  }

  formatDistance(meters: number): string {
    if (meters < 1000) {
      return `${Math.round(meters)} m`;
    } else {
      return `${(meters / 1000).toFixed(1)} km`;
    }
  }
}
