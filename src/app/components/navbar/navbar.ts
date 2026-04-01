import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Router, RouterModule } from '@angular/router';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule, RouterModule],
  templateUrl: './navbar.html',
})
export class NavbarComponent implements OnInit {
  /** Emette la stringa cercata quando l'utente preme Cerca */
  @Output() search = new EventEmitter<string>();

  searchQuery: string = '';

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private router: Router,
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());
  }

  get showSearch(): boolean {
    return this.router.url.startsWith('/stop') || this.router.url.startsWith('/line');
  }

  get searchPlaceholder(): string {
    return this.router.url.startsWith('/line') ? 'search.linePlaceholder' : 'search.placeholder';
  }

  onSearch() {
    if (!this.searchQuery.trim()) return;
    this.search.emit(this.searchQuery.trim());
  }
}
