%define dir /usr/libexec/argo/probes/ams-publisher

Name:      argo-probe-ams-publisher
Summary:   Probe checking AMS publisher.
Version:   0.1.0
Release:   1%{?dist}
License:   ASL 2.0
Source0:   %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Group:     Network/Monitoring
BuildArch: noarch

%description
This package includes probes that check AMS publisher component.

%prep
%setup -q

%build
%{py3_build}

%install
rm -rf %{buildroot}
%{py3_install "--record=INSTALLED_FILES" }

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root,-)
%{python3_sitelib}/argo_probe_ams_publisher
%{dir}


%changelog
* Fri Jun 10 2022 Katarina Zailac <kzailac@gmail.com> - 0.1.0-1%{?dist}
- AO-650 Harmonize argo-mon probes
