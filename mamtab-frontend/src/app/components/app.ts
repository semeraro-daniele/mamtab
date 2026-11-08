import { Component, ViewEncapsulation, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Navbar } from '../shared/nav-bar/nav-bar';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Navbar],
  templateUrl: './app.html',
  encapsulation: ViewEncapsulation.None,
})
export class App { }
