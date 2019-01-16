Summary: NAUTA Kubernetes client metadata v%{_nauta_version} package
Name: nauta-kubernetes-client
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools

Requires: nauta-commons

Requires: nauta-kubernetes-kubectl = %{version}

%define  debug_package %{nil}

%description
%{summary}

%prep

%build

%install

%clean

%files
