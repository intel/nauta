Summary: DLS4E Kubernetes worker metadata v%{_dls4e_version} package
Name: dls4e-kubernetes-worker
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools

Requires: dls4e-commons

Requires: dls4e-kubernetes-kubelet = %{version}

%define  debug_package %{nil}

%description
%{summary}

%prep

%build

%install

%clean

%files
