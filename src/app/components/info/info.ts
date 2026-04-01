import { Component, OnInit } from '@angular/core';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-info',
  imports: [TranslateModule],
  templateUrl: './info.html',
})
export class Info implements OnInit {
  private clickCount = 0;
  private clickTimeout: any;

  showEasterEgg = false;

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());
  }

  handleClick() {
    this.clickCount++;

    // reset timer per click consecutivi
    clearTimeout(this.clickTimeout);
    this.clickTimeout = setTimeout(() => {
      this.clickCount = 0;
    }, 1000);

    if (this.clickCount === 5) {
      this.showEasterEgg = true;
      this.clickCount = 0;

      // nasconde dopo 3 secondi
      setTimeout(() => {
        this.showEasterEgg = false;
      }, 3000);
    }
  }
}
