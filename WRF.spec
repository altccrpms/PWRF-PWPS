%bcond_with pgf

%if %{with pgf}
%global fortran pgf
%global _name_suffix -pgf
Prefix:         /opt/%{name}-%{version}
%else
%global fortran gfortran
%endif

Name:           WRF-WPS%{?_name_suffix}
Version:        3.6.1
Release:        1%{?dist}
Summary:        WRF Model and WPS tools

Group:          Scientific
License:        Public Domain
URL:            http://www.wrf-model.org/
Source0:        http://www2.mmm.ucar.edu/wrf/src/WRFV%{version}.TAR.gz
Patch1:         wps-3.0.1-signal.patch
# Fix linking against netcdf
Patch2:         WRF-WPS-netcdf.patch
#This was created using the configure script and then modifying the 
#result to fix the netcdf locations $(WRF_SRC_ROOT_DIR)/netcdf_links
Source1:        configure.wrf-gfortran
Source2:        configure.wrf-pgf
Source3:        setupwrf
Source10:       http://www2.mmm.ucar.edu/wrf/src/WPSV%{version}.TAR.gz
#This was created using the configure script and then modifying the
#result to fix the netcdf locations $(WRF_SRC_ROOT_DIR)/netcdf_links
Source11:        configure.wps-gfortran
Source12:        configure.wps-pgf-grib2
Source13:        configure.wps-gfortran-dmpar-grib2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  tcsh
BuildRequires:  m4
#gfortran on EL5 fails
BuildRequires:  gcc-gfortran
BuildRequires:  jasper-devel
BuildRequires:  libpng-devel
BuildRequires:  ncarg-devel
BuildRequires:  netcdf-devel
%if 0%{?fedora} >= 17
BuildRequires:  netcdf-fortran-devel
%endif
BuildRequires:  numactl-devel
BuildRequires:  openmpi-devel

#Requires:       

%description
WRF/WPS build.  They need to be built together which is why we have one
srpm.


%package -n WRF%{?_name_suffix}
Summary:        WRF Model
Group:          Scientific

%description -n WRF%{?_name_suffix}
WRF Model.


%package -n WPS%{?_name_suffix}
Summary:        WPS Tools
Group:          Scientific

%description -n WPS%{?_name_suffix}
WPS Tools.


%prep
%setup -q -c -a 10
#patch1 -p0 -b .signal
#patch2 -p1 -b .netcdf
pushd WRFV3
cp %SOURCE1 configure.wrf
%if %{with pgf}
cp %SOURCE2 configure.wrf
%endif
#openmpi mpif90 wrapper doesn't take the -f90,-cc options
sed -i.openmpi -r -e 's/ -(f90|cc)=.*//' arch/archive_configure.defaults \
                                         arch/configure_new.defaults
mkdir netcdf_links
ln -s %{_includedir} netcdf_links/include
ln -s %{_libdir} netcdf_links/lib
popd
pushd WPS
cp %SOURCE11 configure.wps
%if %{with pgf}
cp %SOURCE12 configure.wps
%endif
#openmpi mpif90 wrapper doesn't take the -f90,-cc options
sed -i.openmpi -r -e 's/ -(f90|cc)=.*//' arch/configure.defaults
mkdir netcdf_links
ln -s %{_includedir} netcdf_links/include
ln -s %{_libdir} netcdf_links/lib
popd


%build
. /etc/profile.d/modules.sh
%if %{with pgf}
module load openmpi-pgf
%else
module load openmpi-%{_arch}
%endif
# This is set by the openmpi module and interferes with the build
unset MPI_LIB
export JASPERINC=%{_includedir}/jasper
export JASPERLIB=%{_libdir}
export NCARG_LIB=%{_libdir}/ncarg
pushd WRFV3
./compile em_real
popd
pushd WPS
./compile
popd


%install
rm -rf $RPM_BUILD_ROOT
pushd WRFV3
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp -a main/*.exe $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/WRFV3/test
cp -a run $RPM_BUILD_ROOT%{_datadir}/WRFV3
rm $RPM_BUILD_ROOT%{_datadir}/WRFV3/run/*.exe \
   $RPM_BUILD_ROOT%{_datadir}/WRFV3/run/namelist.input
cp -a test/em_real $RPM_BUILD_ROOT%{_datadir}/WRFV3/test
rm $RPM_BUILD_ROOT%{_datadir}/WRFV3/test/em_real/*.exe
popd
pushd WPS
cp -a */src/*.exe $RPM_BUILD_ROOT%{_bindir}
popd
cp -a %SOURCE3 $RPM_BUILD_ROOT%{_bindir}/setupwrf


%clean
rm -rf $RPM_BUILD_ROOT


%files -n WRF%{?_name_suffix}
%defattr(-,root,root,-)
%doc
%{_bindir}/ndown.exe
%{_bindir}/nup.exe
%{_bindir}/tc.exe
%{_bindir}/real.exe
%{_bindir}/wrf.exe
%{_bindir}/setupwrf
%{_datadir}/WRFV3

%files -n WPS%{?_name_suffix}
%defattr(-,root,root,-)
%doc
%{_bindir}/avg_tsfc.exe
%{_bindir}/calc_ecmwf_p.exe
%{_bindir}/g1print.exe
%{_bindir}/g2print.exe
%{_bindir}/geogrid.exe
%{_bindir}/height_ukmo.exe
%{_bindir}/metgrid.exe
%{_bindir}/mod_levs.exe
%{_bindir}/plotfmt.exe
%{_bindir}/plotgrids.exe
%{_bindir}/rd_intermediate.exe
%{_bindir}/ungrib.exe


%changelog
* Thu Dec 11 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-2
- Move WRF install to %{_bindir} and %{_datadir}/WRFV3
- Add setupwrf

* Thu Nov 20 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-1
- Combinded WRF/WPS
