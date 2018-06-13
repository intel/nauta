min_code_coverage=80

go test -coverprofile=cmd_cov.dat ./cmd/...
cmd_coverage=`go tool cover -func=cmd_cov.dat | grep total | awk -F' '  '{print $NF}'`
rm cmd_cov.dat

go test -coverprofile=pkg_cov.dat ./pkg/...
pkg_coverage=`go tool cover -func=pkg_cov.dat | grep total | awk -F' '  '{print $NF}'`
rm pkg_cov.dat

echo 'Code coverage:'
echo 'cmd module : ' $cmd_coverage
echo 'pkg module : ' $pkg_coverage

if (( $(awk 'BEGIN {print ("'$cmd_coverage'" < "'$min_code_coverage'")}') || 
      $(awk 'BEGIN {print ("'$pkg_coverage'" < "'$min_code_coverage'")}') )); then
  echo 'Code coverage is too low'
  exit 1
fi

