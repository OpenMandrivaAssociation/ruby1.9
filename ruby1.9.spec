%define subver 1.9
%define rubyver 1.9.3
%define patchversion p0
%define rel 1

Summary:	Object Oriented Script Language
Name:		ruby%{subver}
Version:	%{rubyver}.%{patchversion}
Release: 	%mkrel %rel
License:	Ruby or GPLv2
Group:		Development/Ruby
BuildRequires:	autoconf
BuildRequires:	byacc
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	tcl-devel tk-devel
BuildRequires:	db-devel
BuildRequires:  libgdbm-devel >= 1.8.3
BuildRequires:  openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	yaml-devel
BuildRequires:	ruby
BuildRequires:	bison
Source0:	ftp://ftp.ruby-lang.org/pub/ruby/%{subver}/ruby-%{rubyver}-%{patchversion}.tar.bz2
Source1:	http://www.rubycentral.com/faq/rubyfaqall.html.bz2
Source2:	http://dev.rubycentral.com/downloads/files/ProgrammingRuby-0.4.tar.bz2
Source3:	ruby.macros
Provides:	/usr/bin/ruby%{subver}
Provides:	ruby(abi) = %subver
URL:		https://www.ruby-lang.org/
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%define my_target_cpu %{_target_cpu}
%ifarch ppc
%define my_target_cpu powerpc
%endif
%ifarch ppc64
%define my_target_cpu powerpc64
%endif
%ifarch amd64
%define my_target_cpu x86_64
%endif

%package	doc
Summary:	Documentation for the powerful language Ruby
Group:		Development/Ruby

%package	devel
Summary:	Development file for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{version}

%package	tk
Summary:	Tk extension for the powerful language Ruby
Group:		Development/Ruby
Requires:	%{name} = %{version}

%description
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl).  It is simple, straight-forward, and extensible.

%description	doc
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's documentation

%description	devel
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Ruby's devel files.

%description	tk
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl). It is simple, straight-forward, and extensible.

This package contains the Tk extension for Ruby.

%prep
%setup -q -n ruby-%{rubyver}-%{patchversion}

%build
echo '.text' | gcc -shared -o libdummy.so.0 -xassembler - -ltcl -ltk >& /dev/null && {
  if %{_bindir}/ldd libdummy.so.0 | grep -q "lib\(tcl\|tk\).so"; then
    echo "Your tcl/tk is broken, get one with versioning in the libraries."
    exit 1
  fi
  rm -f libdummy.so.0
}

CFLAGS=`echo %optflags | sed 's/-fomit-frame-pointer//'`
%configure2_5x --enable-shared --disable-rpath \
	--with-soname=%{name} \
	--with-baseruby=%{_bindir}/ruby \
	--with-rubylibprefix=%{_prefix}/lib/%{name} \
	--with-ruby-version=minor --program-suffix=%{subver} \
	--with-sitedir=%_prefix/lib/%{name}/site_ruby \
	--with-vendordir=%_prefix/lib/%{name}/vendor_ruby

%make


%install
rm -rf %buildroot
%makeinstall_std install-doc

install -d %buildroot%{_docdir}/%{name}-%{version}
cp -a COPYING* ChangeLog README* ToDo sample %buildroot%{_docdir}/%{name}-%{version}
bzcat %{SOURCE1} > %buildroot%{_docdir}/%{name}-%{version}/FAQ.html

install -d %buildroot%{_datadir}/emacs/site-lisp
cp -a misc/ruby-mode.el %buildroot%{_datadir}/emacs/site-lisp

install -d %buildroot%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%buildroot%{_sysconfdir}/emacs/site-start.d/%{name}.el
(autoload 'ruby-mode "ruby-mode" "Ruby editing mode." t)
(add-to-list 'auto-mode-alist '("\\\\.rb$" . ruby-mode))
(add-to-list 'interpreter-mode-alist '("ruby" . ruby-mode))
EOF

(cd %buildroot%{_docdir}/%{name}-%{version} ; tar xfj %{SOURCE2} ; cd Pro*; mv -f html/* . ; rm -rf html xml)

# Make the file/dirs list, filtering out tcl/tk and devel files
( cd %buildroot \
  && find usr/lib/%{name}/%{subver} \
          \( -not -type d -printf "/%%p\n" \) \
          -or \( -type d -printf "%%%%dir /%%p\n" \) \
) | egrep -v '/(tcl)?tk|(%{my_target_cpu}-%{_target_os}/.*[ha]$)' > %{name}.list

# Fix scripts permissions and location
find %buildroot sample -type f | file -i -f - | grep text | cut -d: -f1 >text.list
cat text.list | xargs chmod 0644
#  Magic grepping to get only files with '#!' in the first line
cat text.list | xargs grep -n '^#!' | grep ':1:#!' | cut -d: -f1 >shebang.list
cat shebang.list | xargs sed -i -e 's|/usr/local/bin|/usr/bin|; s|\./ruby|/usr/bin/%{name}|'
cat shebang.list | xargs chmod 0755


# Install the rpm macros 
mkdir -p %buildroot%{_sysconfdir}/rpm/macros.d
cp %{SOURCE3} %buildroot%{_sysconfdir}/rpm/macros.d/%name.macros

%check
make test

%clean
rm -rf %buildroot

%if %mdkversion < 200900
%post -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig
%endif

%files -f %{name}.list
%defattr(-, root, root)
%dir %{_docdir}/%{name}-%{version}
%{_docdir}/%{name}-%{version}/README
%{_bindir}/*
%dir %{_prefix}/lib/%{name}/
%{_libdir}/lib%{name}.so.*
%{_prefix}/lib/%{name}/site_ruby
%{_prefix}/lib/%{name}/gems
%{_mandir}/*/*
%{_datadir}/emacs/site-lisp/*
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*
%{_sysconfdir}/rpm/macros.d/%{name}.macros

%files doc
%defattr(-, root, root)
%{_datadir}/ri*
%{_docdir}/%{name}-%{version}/COPYING*
%{_docdir}/%{name}-%{version}/ChangeLog
%{_docdir}/%{name}-%{version}/README.*
%{_docdir}/%{name}-%{version}/FAQ.html
%{_docdir}/%{name}-%{version}/ToDo
%{_docdir}/%{name}-%{version}/sample
%{_docdir}/%{name}-%{version}/ProgrammingRuby*

%files devel
%defattr(-, root, root)
%{_includedir}/ruby-%{subver}
%{_libdir}/lib%{name}-static.a
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/ruby-%{subver}.pc

%files tk
%defattr(-, root, root)
%{_prefix}/lib/%{name}/%{subver}/%{my_target_cpu}-%{_target_os}/tcltk*
%{_prefix}/lib/%{name}/%{subver}/%{my_target_cpu}-%{_target_os}/tk*
%{_prefix}/lib/%{name}/%{subver}/tcltk*
%{_prefix}/lib/%{name}/%{subver}/tk*
