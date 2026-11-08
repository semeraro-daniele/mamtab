import { DOCUMENT } from '@angular/common';
import { Injectable, inject, signal } from '@angular/core';

export type AppTheme = 'light' | 'dark';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly document = inject(DOCUMENT);
  private readonly STORAGE_KEY = 'selectedTheme';
  private readonly DEFAULT_THEME: AppTheme = 'light';
  private readonly AVAILABLE_THEMES: AppTheme[] = ['light', 'dark'];

  private readonly _currentTheme = signal<AppTheme>(this.DEFAULT_THEME);
  readonly currentTheme = this._currentTheme.asReadonly();

  constructor() {
    this.initializeTheme();
  }

  setTheme(theme: AppTheme): void {
    if (!this.isThemeSupported(theme)) {
      console.warn(
        `Theme "${theme}" is not supported. Available themes:`,
        this.AVAILABLE_THEMES,
      );
      return;
    }

    this._currentTheme.set(theme);
    this.applyTheme(theme);
    this.saveTheme(theme);
  }

  getTheme(): AppTheme {
    const savedTheme = this.getSavedTheme();
    return savedTheme && this.isThemeSupported(savedTheme)
      ? savedTheme
      : this.DEFAULT_THEME;
  }

  getAvailableThemes(): AppTheme[] {
    return [...this.AVAILABLE_THEMES];
  }

  isThemeSupported(theme: string): theme is AppTheme {
    return this.AVAILABLE_THEMES.includes(theme as AppTheme);
  }

  private initializeTheme(): void {
    const theme = this.getTheme();
    this._currentTheme.set(theme);
    this.applyTheme(theme);
  }

  private applyTheme(theme: AppTheme): void {
    const themeClasses = ['theme-light', 'theme-dark'];
    const themeClass = `theme-${theme}`;

    this.document.documentElement.classList.remove(...themeClasses);
    this.document.body.classList.remove(...themeClasses);

    this.document.documentElement.classList.add(themeClass);
    this.document.body.classList.add(themeClass);
  }

  private getSavedTheme(): string | null {
    return typeof localStorage !== 'undefined'
      ? localStorage.getItem(this.STORAGE_KEY)
      : null;
  }

  private saveTheme(theme: AppTheme): void {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.STORAGE_KEY, theme);
    }
  }
}
