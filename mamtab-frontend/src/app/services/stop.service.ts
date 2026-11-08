import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { StopsResponse, NearbyStopsResponse } from '../models/stop';

@Injectable({
  providedIn: 'root',
})
export class StopService {
  private url = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getById(stopId: string): Observable<StopsResponse> {
    return this.http.get<StopsResponse>(`${this.url}/stops/${encodeURIComponent(stopId)}`);
  }

  getNearby(lat: number, lon: number, radius: number = 500): Observable<NearbyStopsResponse> {
    const params = new HttpParams()
      .set('lat', lat.toString())
      .set('lon', lon.toString())
      .set('radius', radius.toString());
    return this.http.get<NearbyStopsResponse>(`${this.url}/stops/nearby`, { params });
  }
}
