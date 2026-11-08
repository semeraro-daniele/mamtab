import { Routes } from '@angular/router';
import { Homepage } from './components/homepage/homepage';
import { SearchByStop } from './components/search-by-stop/search-by-stop';
import { SearchByLine } from './components/search-by-line/search-by-line';
import { ListLines } from './components/list-lines/list-lines';
import { NearbyStops } from './components/nearby-stops/nearby-stops';
import { Info } from './components/info/info';
import { ErrorPage } from './shared/error-page/error-page';

export const routes: Routes = [
  { path: '', redirectTo: 'homepage', pathMatch: 'full' },
  { path: 'homepage', component: Homepage },
  { path: 'stop', component: SearchByStop },
  { path: 'stop/:id', component: SearchByStop },
  { path: 'line', component: SearchByLine },
  { path: 'line/:id', component: SearchByLine },
  { path: 'list-lines', component: ListLines },
  { path: 'nearby', component: NearbyStops },
  { path: 'info', component: Info },
  { path: '**', pathMatch: 'full', component: ErrorPage },
];
