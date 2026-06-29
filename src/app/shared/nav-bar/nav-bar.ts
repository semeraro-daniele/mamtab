import { CommonModule } from '@angular/common';
import { Component, OnInit, ViewEncapsulation, inject } from '@angular/core';
import { NavigationStart, Router, RouterModule } from '@angular/router';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';
import { AppTheme, ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, TranslateModule, RouterModule],
  templateUrl: './nav-bar.html',
  encapsulation: ViewEncapsulation.None,
})
export class Navbar implements OnInit {
  private readonly languageService = inject(LanguageService);
  private readonly translate = inject(TranslateService);
  private readonly router = inject(Router);
  private readonly themeService = inject(ThemeService);

  infoMenuOpen = false;

  ngOnInit(): void {
    this.translate.use(this.languageService.getLanguage());

    this.router.events.subscribe((event) => {
      if (event instanceof NavigationStart) {
        this.infoMenuOpen = false;
      }
    });
  }

  get currentLanguage(): string {
    return this.languageService.getLanguage();
  }

  get currentTheme(): AppTheme {
    return this.themeService.currentTheme();
  }

  isActive(path: string): boolean {
    return (
      this.router.url === path ||
      this.router.url.startsWith(path + '/') ||
      this.router.url.startsWith(path + '?')
    );
  }

  toggleInfoMenu(): void {
    this.infoMenuOpen = !this.infoMenuOpen;
  }

  changeTheme(theme: AppTheme): void {
    this.themeService.setTheme(theme);
  }

  changeLanguage(language: string): void {
    this.languageService.setLanguage(language);
    this.translate.use(this.languageService.getLanguage());
  }
}
