import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { StopsResponse } from '../models/stop';

@Injectable({
  providedIn: 'root',
})
export class StopService {
  private url = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getById(stopId: string): Observable<StopsResponse> {
    return this.http.get<StopsResponse>(`${this.url}/stops/${encodeURIComponent(stopId)}`);
  }
}
