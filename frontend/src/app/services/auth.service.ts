import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private router: Router, private http: HttpClient) {}

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh');
  }

  setTokens(access: string, refresh: string): void {
    localStorage.setItem('token', access);
    localStorage.setItem('refresh', refresh);
  }

  refreshToken(): Observable<boolean> {
    const refresh = this.getRefreshToken();
    if (!refresh) {
      this.logout();
      return new Observable(subscriber => {
        subscriber.next(false);
        subscriber.complete();
      });
    }

    return new Observable(subscriber => {
      this.http.post<{ access: string }>('http://localhost:8000/api/token/refresh/', { refresh })
        .subscribe({
          next: (response) => {
            localStorage.setItem('token', response.access);
            subscriber.next(true);
            subscriber.complete();
          },
          error: () => {
            this.logout();
            subscriber.next(false);
            subscriber.complete();
          }
        });
    });
  }
}