import { CommonModule } from '@angular/common';
import { Component, OnInit, HostListener } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../navbar/navbar';
import {
  LineDirection,
  LineResponse,
  StopLineDeparturesResponse,
  LineInfo,
} from '../../models/line';
import { LineService } from '../../services/line.service';
import { SearchHistoryService, SearchHistoryItem } from '../../services/search-history.service';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-search-by-line',
  standalone: true,
  imports: [CommonModule, NavbarComponent, TranslateModule, FormsModule],
  templateUrl: './search-by-line.html',
})
export class SearchByLine implements OnInit {
  line: LineResponse | null = null;
  searchPerformed = false;
  loading = false;

  activeDirection: number = 0;

  // All lines list
  allLines: LineInfo[] = [];
  loadingLines = false;

  // Recent searches
  recentSearches: SearchHistoryItem[] = [];

  // Modal state
  showModal = false;
  modalLoading = false;
  stopDepartures: StopLineDeparturesResponse | null = null;
  selectedDate: string = '';
  currentStopId: string = '';
  currentStopName: string = '';
  modalError = false;

  // Scroll to top button
  showScrollButton: boolean = false;

  // Filter stops
  showFilterInput: boolean = false;
  stopFilterQuery: string = '';

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private lineService: LineService,
    public searchHistoryService: SearchHistoryService,
    private route: ActivatedRoute,
    private router: Router,
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());

    // Load all available lines
    this.loadLines();

    // Load recent searches
    this.loadRecentSearches();

    this.route.paramMap.subscribe((params) => {
      const id = params.get('id');
      if (id) {
        this.performSearch(id);
      }
    });
  }

  loadRecentSearches() {
    this.recentSearches = this.searchHistoryService.getRecentSearches('line', 4);
  }

  loadLines() {
    this.loadingLines = true;
    this.lineService.getLines().subscribe({
      next: (res) => {
        this.allLines = res.lines;
        this.loadingLines = false;
      },
      error: (err) => {
        console.error('Error loading all lines:', err);
        this.loadingLines = false;
      },
    });
  }

  selectLine(lineNumber: string, routeLongName?: string) {
    this.searchLine(lineNumber, routeLongName);
  }

  selectRecentSearch(item: SearchHistoryItem) {
    this.searchLine(item.query, item.metadata?.routeLongName);
  }

  removeRecentSearch(item: SearchHistoryItem, event: Event) {
    event.stopPropagation();
    this.searchHistoryService.removeSearch('line', item.query);
    this.loadRecentSearches();
  }

  @HostListener('window:scroll', [])
  onWindowScroll() {
    const scrollPosition =
      window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    this.showScrollButton = scrollPosition > 200;
  }

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  get currentDirection(): LineDirection | null {
    return this.line?.directions.find((d) => d.direction_id === this.activeDirection) ?? null;
  }

  get filteredStops() {
    if (!this.currentDirection) return [];

    if (!this.stopFilterQuery.trim()) {
      return this.currentDirection.stops;
    }

    const query = this.stopFilterQuery.toLowerCase().trim();
    return this.currentDirection.stops.filter(
      (stop) =>
        stop.stop_name.toLowerCase().includes(query) ||
        stop.stop_code?.toLowerCase().includes(query),
    );
  }

  toggleFilterInput() {
    this.showFilterInput = !this.showFilterInput;
    if (!this.showFilterInput) {
      this.stopFilterQuery = '';
    }
  }

  clearFilter() {
    this.stopFilterQuery = '';
  }

  searchLine(query: string, routeLongName?: string) {
    this.router.navigate(['/line', query]);
  }

  performSearch(lineId: string, routeLongName?: string) {
    this.loading = true;
    this.line = null;
    this.searchPerformed = true;

    this.lineService.getLineById(lineId).subscribe({
      next: (res) => {
        if (res && res.risultati > 0) {
          this.searchHistoryService.addSearch({
            type: 'line',
            query: lineId,
            metadata: {
              routeShortName: res.route_short_name || undefined,
              routeLongName: routeLongName || res.route_long_name || undefined,
            },
          });
          this.loadRecentSearches();
        }
        if (!res || res.risultati === 0 || !res.directions || res.directions.length === 0) {
          this.line = null;
          this.searchPerformed = true;
          this.loading = false;
          return;
        }

        this.line = res;
        this.activeDirection = res.directions[0]?.direction_id ?? 0;
        this.searchPerformed = true;
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.line = null;
        this.searchPerformed = true;
        this.loading = false;
      },
    });
  }

  openStopDetails(stopId: string, stopName: string) {
    if (!stopId || !this.line) return;

    this.currentStopId = stopId;
    this.currentStopName = stopName;
    this.selectedDate = this.getTodayDate();
    this.showModal = true;

    this.loadStopDepartures();
  }

  onDateChange(event: Event) {
    const input = event.target as HTMLInputElement;
    this.selectedDate = input.value;
    this.loadStopDepartures(this.selectedDate);
  }

  loadStopDepartures(date?: string) {
    if (!this.line) return;

    this.modalLoading = true;
    this.stopDepartures = null;

    const targetDate = date ?? this.selectedDate;

    this.lineService
      .getStopLineDepartures(
        this.currentStopId,
        this.line.route_id,
        this.activeDirection,
        targetDate || undefined,
      )
      .subscribe({
        next: (res) => {
          this.stopDepartures = res;
          this.modalLoading = false;
        },
        error: (err) => {
          console.error('Error loading stop departures:', err);
          this.modalLoading = false;
        },
      });
  }

  getTodayDate(): string {
    const today = new Date();
    return today.toISOString().split('T')[0];
  }

  getMaxDate(): string {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30); // 30 giorni nel futuro
    return maxDate.toISOString().split('T')[0];
  }

  closeModal() {
    this.showModal = false;
    this.stopDepartures = null;
  }

  goToStop(stopId: string) {
    this.closeModal();
    this.router.navigate(['/stop', stopId]);
  }
}
