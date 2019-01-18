Summary: NAUTA Kubernetes server metadata v%{_nauta_version} package
Name: nauta-kubernetes-server
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools

Requires: nauta-commons

Requires: nauta-kubernetes-apiserver = %{version}
Requires: nauta-kubernetes-scheduler = %{version}
Requires: nauta-kubernetes-controller-manager = %{version}

%define  debug_package %{nil}

%description
%{summary}

%prep

%build

%install

%clean

%files
