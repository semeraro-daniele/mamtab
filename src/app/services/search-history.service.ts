import { Injectable } from '@angular/core';

export interface SearchHistoryItem {
  type: 'line' | 'stop';
  query: string;
  timestamp: number;
  metadata?: {
    stopId?: string;
    stopName?: string;
    stopCode?: string;
    routeShortName?: string;
    routeLongName?: string;
  };
}

@Injectable({ providedIn: 'root' })
export class SearchHistoryService {
  private readonly STORAGE_KEY = 'amtab_search_history';
  private readonly MAX_RECENT_ITEMS = 4;

  constructor() {}

  // Aggiunge una ricerca alla cronologia
  addSearch(item: Omit<SearchHistoryItem, 'timestamp'>): void {
    const history = this.getHistory();

    // Rimuove duplicati per type + query
    const filteredHistory = history.filter(
      (h) => !(h.type === item.type && h.query.toLowerCase() === item.query.toLowerCase()),
    );

    const newItem: SearchHistoryItem = {
      ...item,
      timestamp: Date.now(),
    };

    filteredHistory.unshift(newItem);

    const limitedHistory = filteredHistory.slice(0, this.MAX_RECENT_ITEMS * 2);

    this.saveHistory(limitedHistory);
  }

  // Ottiene le ricerche recenti per tipo
  getRecentSearches(
    type: 'line' | 'stop',
    limit: number = this.MAX_RECENT_ITEMS,
  ): SearchHistoryItem[] {
    return this.getHistory()
      .filter((item) => item.type === type)
      .slice(0, limit);
  }

  // Ottiene tutte le ricerche recenti
  getAllRecentSearches(limit: number = this.MAX_RECENT_ITEMS): SearchHistoryItem[] {
    const history = this.getHistory();
    return history.slice(0, limit);
  }

  // Rimuove una ricerca specifica dalla cronologia
  removeSearch(type: 'line' | 'stop', query: string): void {
    const history = this.getHistory();
    const filtered = history.filter(
      (item) => !(item.type === type && item.query.toLowerCase() === query.toLowerCase()),
    );
    this.saveHistory(filtered);
  }

  // Pulisce tutta la cronologia
  clearHistory(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  // Pulisce la cronologia per un tipo specifico
  clearHistoryByType(type: 'line' | 'stop'): void {
    const history = this.getHistory();
    const filtered = history.filter((item) => item.type !== type);
    this.saveHistory(filtered);
  }

  // Ottiene la cronologia completa dal localStorage
  private getHistory(): SearchHistoryItem[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (!stored) return [];

      const parsed = JSON.parse(stored);
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      console.error('Error reading search history:', error);
      return [];
    }
  }

  // Salva la cronologia nel localStorage
  private saveHistory(history: SearchHistoryItem[]): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving search history:', error);
    }
  }
}
