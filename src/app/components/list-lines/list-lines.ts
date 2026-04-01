import { Component, OnInit } from '@angular/core';
import { NavbarComponent } from "../navbar/navbar";

import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-list-lines',
  imports: [TranslateModule, NavbarComponent],
  templateUrl: './list-lines.html',
})
export class ListLines implements OnInit {
  listLines = [
    { name: '01 - Bari Centrale – Santo Spirito', file: '01-Bari Centrale - Santo Spirito .pdf' },
    { name: '02 - Piscine Comunali – Sant’Anna', file: '02_-Piscine Comunali - S_Anna.pdf' },
    {
      name: '02 - Piscine Comunali – C.S. Polivalente',
      file: '02-Piscine Comunali - C.S. Polivalente.pdf',
    },
    {
      name: '03 - Bari Centrale – Ospedale (San Paolo)',
      file: '03-Bari Centrale - Ospedale (S.Paolo).pdf',
    },
    {
      name: '04 - Bari Centrale – Carbonara / Ceglie',
      file: '04-Bari Centrale - Carbonara_Ceglie.pdf',
    },
    {
      name: '06 - Piscine Comunali – Parco Domingo',
      file: '06-Piscine Comunali - Parco Domingo.pdf',
    },
    { name: '07 - Bari Centrale – Deposito Amtab', file: '07-Bari Centrale - Dep. Amtab.pdf' },
    { name: '09 - Policlinico – C.S. Polivalente', file: '09-Policlinico - C.S. Polivalente .pdf' },
    { name: '10 - Parco Domingo – Parco Domingo', file: '10-Parco Domingo - Parco Domingo.pdf' },
    { name: '11 - Bari Centrale – Loseto', file: '11-Bari Centrale - Loseto.pdf' },
    { name: '12 - Bari Centrale – Torre a Mare', file: '12-Bari Centrale - Torre a Mare.pdf' },
    {
      name: '13 - Bari Centrale – Dalfino (San Paolo)',
      file: '13-Bari Centrale - Dalfino (S.Paolo).pdf',
    },
    {
      name: '14 - Oleandri Z.I. – C.S. Polivalente',
      file: '14-Oleandri Z.I. - C.S. Polivalente.pdf',
    },
    { name: '16 - Bari Centrale – Aeroporto', file: '16-Bari Centrale - Aeroporto.pdf' },
    { name: '19 - Bari Centrale – San Pio', file: '19-Bari Centrale - San Pio.pdf' },
    { name: '20 - Bari Centrale – Parco Adria', file: '20-Bari Centrale - Parco Adria.pdf' },
    { name: '21 - Bari Centrale – Ceglie', file: '21-Bari Centrale - Ceglie.pdf' },
    { name: '22 - Piscine Comunali – Mungivacca', file: '22-Piscine Comunali - Mungivacca.pdf' },
    { name: '23 - Circolare Regione Puglia', file: '23-Circolare Regione Puglia.pdf' },
    {
      name: '25 - Luigi di Savoia – Oleandri Z.I.',
      file: '25-Luigi di Savoia - Oleandri Z.I..pdf',
    },
    {
      name: '27 - Piscine Comunali – Parco Domingo',
      file: '27-Piscine Comunali - Parco Domingo.pdf',
    },
    { name: '30 - Loseto – Margherite Z.I.', file: '30-Loseto - Margherite Z.I..pdf' },
    { name: '33 - Deposito Amtab – San Pio', file: '33-Dep. Amtab - San Pio.pdf' },
    {
      name: '35 - Circolare Carrassi – Policlinico',
      file: '35-Circolare Carrassi - Policlinico.pdf',
    },
    {
      name: '42 - Piscine Comunali – P&R Pane e Pomodoro',
      file: '42-Piscine Comunali - P&R Pane&Pomodoro.pdf',
    },
    { name: '50 - Circolare Porto', file: '50-Circolare Porto.pdf' },
    {
      name: '53 - Bari Centrale – De Blasi (San Paolo)',
      file: '53-Bari Centrale - De Blasi (S.Paolo).pdf',
    },
    { name: '61 - San Pio – Margherite Z.I.', file: '61-San Pio - Margherite Z.I..pdf' },
    { name: '71 - Bari Centrale – Santa Caterina', file: '71-Bari Centrale - S.Caterina.pdf' },
    { name: 'A - P&R Vittorio Veneto', file: 'A-P&R V.Veneto.pdf' },
    { name: 'AB - Circolare Notturna', file: 'AB-Circolare Notturna.pdf' },
    { name: 'B - P&R Pane e Pomodoro', file: 'B-P&R Pane Pomodoro.pdf' },
    { name: 'C - P&R 2 Giugno', file: 'C-P&R 2 Giugno .pdf' },
    { name: 'D - Circolare Tribunale', file: 'D-Circolare Tribunale.pdf' },
    { name: 'E - P&R Polipark', file: 'E-P&R Polipark .pdf' },
    { name: 'H - Navetta Policlinico', file: 'H-Navetta Policlinico.pdf' },
    { name: 'PJ - Circolare C.S. Polivalente', file: 'PJ-Circolare C.S. Polivalente .pdf' },
  ];

  constructor(
    private languageService: LanguageService,
    private translate: TranslateService,
  ) {}

  ngOnInit() {
    this.translate.use(this.languageService.getLanguage());
  }

  getLineUrl(file: string): string {
    return `https://muvt.app/libretto/${encodeURIComponent(file)}`;
  }
}
