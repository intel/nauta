Summary: DLS4E Precompiled pip python v%{_dls4e_version} package
Name: dls4e-pip-repository
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define  debug_package %{nil}

%description
%{summary}

%prep

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}/opt/dls4e/pip
pip wheel ansible==2.5.0.0 pip==10.0.1 virtualenv==16.0.0 \
    setuptools==39.2.0 wheel==0.31.1 \
    docker==3.4.0 pyOpenSSL==17.5.0 \
    -w %{buildroot}/opt/dls4e/pip/

exit 0
%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
/opt/dls4e/pip/*
