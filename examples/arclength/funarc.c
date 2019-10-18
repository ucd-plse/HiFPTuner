#include "../../precimonious/logging/cov_log.h"
#include "../../precimonious/logging/cov_checker.h"

#include <time.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>

extern uint64_t current_time_ns(void);
#define ITERS 10

long double fun( long double x )
{
  int k, n = 5;
  long double t1, d1 = 1.0L;

  t1 = x;

  for( k = 1; k <= n; k++ )
  {
    d1 = 2.0 * d1;
    t1 = t1 + sin (d1 * x) / d1;
  }

  return t1;
}

int main()
{
  int l;
  uint64_t start, end;
  long int diff = 0;

  int i, j, k, n = 1000000;
  long double h, t1, t2, dppi, ans = 5.795776322412856L;
  long double s1; 
  long double threshold; 
  long double epsilon = -8.0;

  // dummy calls
  sqrtf(0);
  acosf(0);
  sinf(0);

  start = current_time_ns();
  for (l = 0; l < ITERS; l++)
  {
    t1 = -1.0;
    dppi = acos(t1);
    s1 = 0.0;
    t1 = 0.0;
    h = dppi / n;

    for( i = 1; i <= n; i++ )
    {
      t2 = fun (i * h);
      s1 = s1 + sqrt (h*h + (t2 - t1)*(t2 - t1));
      t1 = t2;
    }
  }
  end = current_time_ns();

  diff = (end-start);

  threshold = s1*pow(10, epsilon);

  // cov_spec_log("spec.cov", threshold, 1, s1);
  cov_log("result", "log.cov", 1, s1);
  cov_check("log.cov", "spec.cov", 1);

  //  printf(" => total error: %d %1.15Le %1.15Le\n", (long double) fabs(ans-s1) > threshold, (long double) fabs(ans-s1), threshold);
  //  printf(" => ans: %1.15Le\n =>  s1: %1.15Le\n", (long double)ans, (long double)s1);

  FILE* file;
  file = fopen("score.cov", "w");
  fprintf(file, "%ld\n", diff);
  fclose(file);

  return 0;

}


