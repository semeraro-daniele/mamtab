import {
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterModule, RouterOutlet } from '@angular/router';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../services/language.service';
import { AppTheme, ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterModule, TranslateModule, CommonModule],
  templateUrl: './app.html',
})
export class App implements OnInit {
  protected readonly title = signal('mamtab');
  private readonly languageService = inject(LanguageService);
  private readonly translate = inject(TranslateService);
  private readonly router = inject(Router);
  private readonly themeService = inject(ThemeService);

  infoMenuOpen = false;

  ngOnInit(): void {
    this.translate.use(this.languageService.getLanguage());
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
    if (this.infoMenuOpen && this.isActive('/info')) {
      // se siamo già sulla pagina info, vai alla pagina invece di aprire il menu
      this.infoMenuOpen = false;
      this.router.navigate(['/info']);
    }
  }

  changeTheme(theme: AppTheme): void {
    this.themeService.setTheme(theme);
  }

  changeLanguage(language: string): void {
    this.languageService.setLanguage(language);
    this.translate.use(this.languageService.getLanguage());
  }
}
