Summary: NAUTA Kubernetes metadata v%{_nauta_version} package
Name: nauta-kubernetes
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools

Requires: nauta-kubernetes-server = %{version}
Requires: nauta-kubernetes-worker = %{version}
Requires: nauta-kubernetes-client = %{version}

%define  debug_package %{nil}

%description
%{summary}

%prep

%build

%install

%clean

%files
