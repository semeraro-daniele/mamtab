import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { Router } from '@angular/router';

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-homepage',
  imports: [TranslateModule],
  templateUrl: './homepage.html',
  encapsulation: ViewEncapsulation.None,
})
export class Homepage implements OnInit {
  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
    private router: Router
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());
  }

  goToLine(): void {
    this.router.navigate(['/line']);
  }

  goToStop(): void {
    this.router.navigate(['/stop']);
  }

  goToNearby(): void {
    this.router.navigate(['/nearby']);
  }
}
