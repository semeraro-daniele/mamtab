import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { LineResponse, StopLineDeparturesResponse, LinesResponse } from '../models/line';

@Injectable({ providedIn: 'root' })
export class LineService {
  private url = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getLines(): Observable<LinesResponse> {
    return this.http.get<LinesResponse>(`${this.url}/lines`);
  }

  getLineById(lineId: string): Observable<LineResponse> {
    return this.http.get<LineResponse>(`${this.url}/lines/${encodeURIComponent(lineId)}`);
  }

  getStopLineDepartures(
    stopId: string,
    line: string,
    directionId: number,
    date?: string,
  ): Observable<StopLineDeparturesResponse> {
    const dateSegment = date ? `/${encodeURIComponent(date)}` : '';
    return this.http.get<StopLineDeparturesResponse>(
      `${this.url}/lines/${encodeURIComponent(line)}/stops/${encodeURIComponent(stopId)}/departures/${directionId}${dateSegment}`,
    );
  }
}
