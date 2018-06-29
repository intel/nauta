Summary: DLS4E Kubernetes metadata v%{_dls4e_version} package
Name: dls4e-kubernetes
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools

Requires: dls4e-kubernetes-server = %{version}
Requires: dls4e-kubernetes-worker = %{version}
Requires: dls4e-kubernetes-client = %{version}

%define  debug_package %{nil}

%description
%{summary}

%prep

%build

%install

%clean

%files
