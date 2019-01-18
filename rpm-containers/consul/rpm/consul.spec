Summary: NAUTA Consul v1.0.6 package
Name: nauta-consul
Version: 1.1.0
Release: 0
License: MPL-2.0
Group: Tools
SOURCE0 : consul.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define  debug_package %{nil}

%description
%{summary}

%prep
%setup -q -n consul

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}%{_bindir}
cp -a consul %{buildroot}%{_bindir}/consul


%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
%{_bindir}/consul
