import { CommonModule } from '@angular/common';
import { Component, OnInit, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../navbar/navbar';
import { Stop, Departure } from '../../models/stop';
import { StopService } from '../../services/stop.service';
import { SearchHistoryService, SearchHistoryItem } from '../../services/search-history.service';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-seach-by-stop',
  standalone: true,
  imports: [CommonModule, NavbarComponent, TranslateModule],
  templateUrl: './search-by-stop.html'
})
export class SearchByStop implements OnInit {
  stops: Stop[] = [];
  searchPerformed: boolean = false;
  loading: boolean = false;
  expandedStops: Set<string> = new Set();
  showScrollButton: boolean = false;

  // Lazy loading
  visibleDeparturesPerStop: Map<string, number> = new Map();
  private departuresPerPage = 5;

  // Recent searches
  recentSearches: SearchHistoryItem[] = [];

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private stopService: StopService,
    public searchHistoryService: SearchHistoryService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());

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
    this.recentSearches = this.searchHistoryService.getRecentSearches('stop', 4);
  }

  selectRecentSearch(item: SearchHistoryItem) {
    this.searchStop(item.query);
  }

  removeRecentSearch(item: SearchHistoryItem, event: Event) {
    event.stopPropagation();
    this.searchHistoryService.removeSearch('stop', item.query);
    this.loadRecentSearches();
  }

  @HostListener('window:scroll', [])
  onWindowScroll() {
    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    this.showScrollButton = scrollPosition > 200;
  }

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  goToLine(line: string | null) {
    if (!line) return;
    this.router.navigate(['/line', line]);
  }

  searchStop(query: string) {
    this.router.navigate(['/stop', query]);
  }

  performSearch(stopId: string) {
    this.loading = true;
    this.stops = [];
    this.searchPerformed = true;
    this.visibleDeparturesPerStop.clear();

    this.stopService.getById(stopId).subscribe({
      next: (res) => {
        this.stops = res.stops;
        this.expandedStops = new Set(this.stops.map((s) => s.stop_id));
        
        // Inizializza il numero di partenze visibili per ogni fermata (5 per default)
        this.stops.forEach((stop) => {
          this.visibleDeparturesPerStop.set(stop.stop_id, this.departuresPerPage);
        });

        this.loading = false;

        if (res.stops.length > 0) {
          const firstStop = res.stops[0];
          this.searchHistoryService.addSearch({
            type: 'stop',
            query: stopId,
            metadata: {
              stopId: firstStop.stop_id,
              stopName: firstStop.stop_name,
              stopCode: firstStop.stop_code || undefined,
            },
          });
          this.loadRecentSearches();
        }
      },
      error: (err) => {
        console.error(err);
        this.stops = [];
        this.loading = false;
      },
    });
  }

  isExpanded(stopId: string | undefined): boolean {
    if (!stopId) return false;
    return this.expandedStops.has(stopId);
  }

  toggleExpand(stopId: string | undefined) {
    if (!stopId) return;
    if (this.expandedStops.has(stopId)) this.expandedStops.delete(stopId);
    else this.expandedStops.add(stopId);
  }

  getVisibleDepartures(stop: Stop): Departure[] {
    const visibleCount = this.visibleDeparturesPerStop.get(stop.stop_id) || this.departuresPerPage;
    return stop.lines.slice(0, visibleCount);
  }

  hasMoreDepartures(stop: Stop): boolean {
    const visibleCount = this.visibleDeparturesPerStop.get(stop.stop_id) || this.departuresPerPage;
    return visibleCount < stop.lines.length;
  }

  loadMoreDepartures(stopId: string | undefined) {
    if (!stopId) return;
    const current = this.visibleDeparturesPerStop.get(stopId) || this.departuresPerPage;
    this.visibleDeparturesPerStop.set(stopId, current + this.departuresPerPage);
  }
}
