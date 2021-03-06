# vim: sw=4:ts=4:et
#
# Copyright 2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

%global base_name katello
%global katello_requires python-iniparse python-simplejson python-kerberos m2crypto python-dateutil
%global locale_dir /usr/share/locale/
%global homedir %{_datarootdir}/%{base_name}

Name:          %{base_name}-cli
Summary:       Client package for managing application life-cycle for Linux systems
Group:         Applications/System
License:       GPLv2
URL:           http://www.katello.org
Version:       1.3.4
Release:       1%{?dist}
Source0:       https://fedorahosted.org/releases/k/a/katello/%{name}-%{version}.tar.gz
Requires:      %{base_name}-cli-common
BuildArch:     noarch
BuildRequires: spacewalk-pylint
BuildRequires: translate-toolkit
Obsoletes:     katello-cli-headpin < 1.0.1-1
Provides:      katello-cli-headpin = 1.0.1-1

%description
Provides a client package for managing application life-cycle for
Linux systems with Katello

%package common
Summary:       Common Katello client bits
Group:         Applications/System
License:       GPLv2
Requires:      %{katello_requires}
BuildRequires: python2-devel
BuildRequires: gettext
BuildRequires: /usr/bin/pod2man
BuildRequires: %{katello_requires}

BuildArch:     noarch

%description common
Common classes for katello clients


%package unit-tests
Summary:       Unit tests for Katello client
Group:         Applications/System
License:       GPLv2
Requires:      python-kerberos
Requires:      m2crypto
Requires:      python-nose
Requires:      python-mock
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description unit-tests
Unit tests for Katello client.
For more info see:
https://fedorahosted.org/katello/wiki/TestingHowto

%prep
%setup -q

%build
%if ! 0%{?fastbuild:1}
    PYTHONPATH=src/ pylint --rcfile=/etc/spacewalk-pylint.rc --additional-builtins=_ katello
%endif

# check for malformed gettext strings
scripts/check-gettext.sh

# generate usage docs and incorporate it into the man page
pushd man
PYTHONPATH=../src python ../scripts/usage.py "katello" >katello-usage.txt
PYTHONPATH=../src python ../scripts/usage.py "headpin" >headpin-usage.txt
sed -e '/^THE_USAGE/{r katello-usage.txt' -e 'd}' katello.pod |\
    sed -e 's/THE_VERSION/%{version}/g' |\
    /usr/bin/pod2man --name=katello -c "Katello Reference" --section=1 --release=%{version} - katello.man1
sed -e '/^THE_USAGE/{r headpin-usage.txt' -e 'd}' headpin.pod |\
    sed -e 's/THE_VERSION/%{version}/g' |\
    /usr/bin/pod2man --name=headpin -c "Headpin Reference" --section=1 --release=%{version} - headpin.man1
sed -e 's/THE_VERSION/%{version}/g' katello-debug-certificates.pod |\
/usr/bin/pod2man --name=katello -c "Katello Reference" --section=1 --release=%{version} - katello-debug-certificates.man1
popd

#check locale file
for i in po/*.po; do
    msgfmt -c $i
    FILE=$(mktemp)
    # TODO - enable endwhitespace, endpunc, puncspacing, options filters
    pofilter --nofuzzy -t variables -t blank -t urls -t emails -t long -t newlines \
        -t printf -t validchars --gnome $i | tee $FILE
    grep msgid $FILE >/dev/null && exit 1
    rm $FILE
done

# create locale files
make -C po all-mo

%install
install -d %{buildroot}%{_bindir}/
install -d %{buildroot}%{_sysconfdir}/%{base_name}/
install -d %{buildroot}%{python_sitelib}/%{base_name}
install -d %{buildroot}%{python_sitelib}/%{base_name}/client
install -d %{buildroot}%{python_sitelib}/%{base_name}/client/api
install -d %{buildroot}%{python_sitelib}/%{base_name}/client/cli
install -d %{buildroot}%{python_sitelib}/%{base_name}/client/core
install -d %{buildroot}%{python_sitelib}/%{base_name}/client/lib
install -d %{buildroot}%{python_sitelib}/%{base_name}/client/lib/ui
install -d %{buildroot}%{python_sitelib}/%{base_name}/client/lib/utils
install -pm 0644 bin/%{base_name} %{buildroot}%{_bindir}/%{base_name}
install -pm 0644 bin/_complete_%{base_name} %{buildroot}%{_bindir}/_complete_%{base_name}
install -pm 0644 bin/%{base_name}-debug-certificates %{buildroot}%{_bindir}/%{base_name}-debug-certificates
install -pm 0644 etc/client.conf %{buildroot}%{_sysconfdir}/%{base_name}/client.conf
install -Dp -m0644 etc/%{base_name}.completion.sh %{buildroot}%{_sysconfdir}/bash_completion.d/%{base_name}
install -pm 0644 src/%{base_name}/*.py %{buildroot}%{python_sitelib}/%{base_name}/
install -pm 0644 src/%{base_name}/client/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/
install -pm 0644 src/%{base_name}/client/api/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/api/
install -pm 0644 src/%{base_name}/client/cli/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/cli/
install -pm 0644 src/%{base_name}/client/core/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/core/
install -pm 0644 src/%{base_name}/client/lib/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/lib/
install -pm 0644 src/%{base_name}/client/lib/ui/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/lib/ui/
install -pm 0644 src/%{base_name}/client/lib/utils/*.py %{buildroot}%{python_sitelib}/%{base_name}/client/lib/utils/
install -d -m 0755 %{buildroot}%{_mandir}/man1
install -m 0644 man/%{base_name}.man1 %{buildroot}%{_mandir}/man1/%{base_name}.1
install -m 0644 man/headpin.man1 %{buildroot}%{_mandir}/man1/headpin.1
install -m 0644 man/%{base_name}-debug-certificates.man1 %{buildroot}%{_mandir}/man1/%{base_name}-debug-certificates.1

# install locale files
for lang in $(ls po/*.po); do
    code=$(basename "$lang" ".po")
    install -d %{buildroot}%{locale_dir}/${code}/LC_MESSAGES/
    install -pm 0644 po/${code}.mo %{buildroot}%{locale_dir}/${code}/LC_MESSAGES/%{base_name}-cli.mo
done
%find_lang %{name}

# several scripts are executable
chmod 755 %{buildroot}%{python_sitelib}/%{base_name}/client/main.py

mkdir -p %{buildroot}%{homedir}/tests/%{name}/unit-tests
sed -i -e 's|\.\./src/katello|%{python_sitelib}/%{base_name}|g' test/katello/__init__.py
cp -ap test/katello %{buildroot}%{homedir}/tests/%{name}/unit-tests

pushd %{buildroot}%{_bindir}
ln -svf %{_bindir}/%{base_name} headpin
popd

%files
%attr(755,root,root) %{_bindir}/%{base_name}
%attr(755,root,root) %{_bindir}/_complete_%{base_name}
%attr(755,root,root) %{_bindir}/headpin
%attr(755,root,root) %{_bindir}/%{base_name}-debug-certificates
%config(noreplace) %{_sysconfdir}/%{base_name}/client.conf
%{_sysconfdir}/bash_completion.d/%{base_name}
%doc README LICENSE
%{_mandir}/man1/%{base_name}.1*
%{_mandir}/man1/headpin.1*
%{_mandir}/man1/%{base_name}-debug-certificates.1*

%files common -f %{name}.lang
%dir %{_sysconfdir}/%{base_name}
%{python_sitelib}/%{base_name}/

%files unit-tests
%{homedir}/tests

%clean
# clean locale files
make -C po clean

%changelog
* Wed Jan 30 2013 Justin Sherrill <jsherril@redhat.com> 1.3.4-1
- removing pulpv2 prefix from pulpv2 branch (jsherril@redhat.com)
- 880125 - Errors message when no key can be found (ares@igloonet.cz)
- smart proxies - listing available features in cli info
  (tstrachota@redhat.com)
- 875117 - fix in msg when repo not found in CLI (tstrachota@redhat.com)
- 839584 - cli system_group info should show max allowed systems
  (tstrachota@redhat.com)
- comp. res. cli - pylint fixes (tstrachota@redhat.com)
- comp. res. cli - deleting (tstrachota@redhat.com)
- comp. res. cli - updating (tstrachota@redhat.com)
- comp. res. cli - create (tstrachota@redhat.com)
- comp. res. cli - actions list and info (tstrachota@redhat.com)
- cli - case insensitive choices for optparse options (tstrachota@redhat.com)
- 895735 - [RFE] Specifying the keyname when removing custom info from a system
  should be required (komidore64@gmail.com)
- Automatic commit of package [katello-cli] release [1.3.3-1].
  (jsherril@redhat.com)
- Translations - Update .po and POTFILES.in files for katello-cli.
  (jsherril@redhat.com)
- Translations - Download translations from Transifex for katello-cli.
  (jsherril@redhat.com)
- 894480 - remove PyXML dependency (msuchy@redhat.com)
- resolve pylint errors on Fedora 19 (msuchy@redhat.com)
- Revert "Pylint - Updates to remove disablement of pylint warnings present in"
  (msuchy@redhat.com)
- cli completion - fix in sed expression (tstrachota@redhat.com)
- fix config_template info formatting (pchalupa@redhat.com)
- Cli Fix (jhadvig@gmail.com)
- 886462 - [cli] ping returns $? == 30 (but all services are OK)
  (komidore64@gmail.com)
- 853385: Display the environment in the output of system info
  (komidore64@gmail.com)
- fricken pylint (komidore64@gmail.com)
- unifying "blah blah blah [ %%s ]" in CLI" (komidore64@gmail.com)
- 879151, 879161, 879169, 879174, 879195, 880031, 880048, 880054, 880066,
  880073, 880089, 880131, 880566 (komidore64@gmail.com)
- 879151, 879161, 879169, 879174, 879195, 880031, 880048, 880054, 880066,
  880073, 880089, 880131, 880566 (komidore64@gmail.com)
-  Adding environment tests in CLI (jomara@redhat.com)
- fixing zh_TW.po (msuchy@redhat.com)
- fix pt.po (msuchy@redhat.com)
- fix ko.po (msuchy@redhat.com)
- fixing ko.po (msuchy@redhat.com)
- fix zh_CN.po (msuchy@redhat.com)
- update pt.po (msuchy@redhat.com)
- fix ru.po (msuchy@redhat.com)
- fix ja.po (msuchy@redhat.com)
- fix zh_TW.po (msuchy@redhat.com)
- forward port translation from SAM (msuchy@redhat.com)
- Adding environment name change to CLI (jomara@redhat.com)
- 876248: Successful actions should be logged as info, not as errors
  (bkearney@redhat.com)

* Tue Jan 15 2013 Justin Sherrill <jsherril@redhat.com> 1.3.3-1
- Translations - Update .po and POTFILES.in files for katello-cli.
  (jsherril@redhat.com)
- Translations - Download translations from Transifex for katello-cli.
  (jsherril@redhat.com)
- 894480 - remove PyXML dependency (msuchy@redhat.com)
- resolve pylint errors on Fedora 19 (msuchy@redhat.com)
- Revert "Pylint - Updates to remove disablement of pylint warnings present in"
  (msuchy@redhat.com)
- cli completion - fix in sed expression (tstrachota@redhat.com)
- fix config_template info formatting (pchalupa@redhat.com)

* Tue Jan 08 2013 Lukas Zapletal <lzap+git@redhat.com> 1.3.2-1
- Merge pull request #1341 from komidore64/cli-ping
- 886462 - [cli] ping returns $? == 30 (but all services are OK)
- 853385: Display the environment in the output of system info
- fricken pylint
- unifying "blah blah blah [ %%s ]" in CLI" (komidore64@gmail.com)
- 879151, 879161, 879169, 879174, 879195, 880031, 880048, 880054, 880066,
  880073, 880089, 880131, 880566
- Merge pull request #1322 from jsomara/envname
-  Adding environment tests in CLI
- fixing locales
- forward port translation from SAM
- Adding environment name change to CLI
- 876248: Successful actions should be logged as info, not as errors

* Tue Dec 18 2012 Miroslav Suchý <msuchy@redhat.com> 1.3.1-1
- smart proxies - cli CRUD actions (tstrachota@redhat.com)
- cli - packaged completion script (tstrachota@redhat.com)
- cli - python based shell completion (tstrachota@redhat.com)
- Bumping package versions for 1.3. (ehelms@redhat.com)

* Thu Dec 06 2012 Eric D Helms <ehelms@redhat.com> 1.2.2-1
- correcting activation key help message for cli (komidore64@gmail.com)
- Switched to python or (jomara@redhat.com)
- 879245 - optionally displaying uuid instead of name (jomara@redhat.com)
- 879561 - Throw exception if system not found (daviddavis@redhat.com)
- 879320 - removing ipv4 address from system list (jomara@redhat.com)
- 866972 - katello-debug needs to take headpin into consideration
  (komidore64@gmail.com)
- subnet cli - CRUD actions (tomas.str@gmail.com)
- cli utils - fix in unnest_one (tstrachota@redhat.com)
- 875609-hypervisor - allow hypervisors to successfully register and list in
  katello (thomasmckay@redhat.com)
- 874280 - terminology changes for consistency across subman, candlepin, etc
  (jomara@redhat.com)
- Translations - Update .po and POTFILES.in files for katello-cli.
  (ehelms@redhat.com)
- Translations - New translations from Transifex for katello-cli.
  (ehelms@redhat.com)
- Translations - Download translations from Transifex for katello-cli.
  (ehelms@redhat.com)
- simplify code (msuchy@redhat.com)
- code cleanup (msuchy@redhat.com)
- 798675 - display "required" if option is required (msuchy@redhat.com)
- 871622 - correctly set provides and obsoletes (msuchy@redhat.com)
- Revert "871622 - fixing obsoletes to correctly upgrade from katello-cli-
  headpin" (msuchy@redhat.com)
- 871622 - fixing obsoletes to correctly upgrade from katello-cli-headpin
  (jomara@redhat.com)
- 863461 - Headpin Cli automation : Failure to list the org updated with
  special chars other than ascii chars (komidore64@gmail.com)
- fixing pylint error (lzap+git@redhat.com)
- 865528 - improving error handling in the cli code (lzap+git@redhat.com)
- cli - method batch_add_columns applied (tstrachota@redhat.com)
- cli printer - tests and utils (tstrachota@redhat.com)
- 871622 - correctly set version in obsolete (msuchy@redhat.com)
- Pylint - Updates to remove disablement of pylint warnings present in 0.26
  since pylint 0.25 is what is available in Fedora. (ehelms@redhat.com)
- Pylint - Fixes a regex and silences the anonmolous backlash warnings from the
  color declarations in the Spinner. (ehelms@redhat.com)
- CLI Unittest - Fixes issue where CLI unittests couldn't pass on a clean
  system by mocking the get_katello_mode call. (ehelms@redhat.com)
- cli config - fix for missing section in get_katello_mode
  (tstrachota@redhat.com)
- Travis - Adds first pass at a Travis configuration. (ericdhelms@gmail.com)
- 865571 - man page for headpin shows katello context (komidore64@gmail.com)
- 869575 - CLI - changeset - fix error during add/remove repo/pkg/errata
  (bbuckingham@redhat.com)
- 869575 - changeset add_product - correctly handle product request
  (bbuckingham@redhat.com)
- forgot to check with pylint (komidore64@gmail.com)
- 818903 - Name of the pdf generated for headpin system report command should
  be modified (komidore64@gmail.com)
- RAM entitlements (jomara@redhat.com)
- 855267 - fix string issue raised in pull request review
  (bbuckingham@redhat.com)
- 855267 - changeset - moving common logic for product opts to a class method
  (bbuckingham@redhat.com)
- fixing busted cli tests (komidore64@gmail.com)
- 855267 - fix few strings based on pull request review
  (bbuckingham@redhat.com)
- 855267 - CLI - pylint, template and changeset fixes (bbuckingham@redhat.com)
- 855267 - fixes for pylint errors (bbuckingham@redhat.com)
- 859892 - system info contains "u"-s in "OS release" field
  (komidore64@gmail.com)
- 855267 - CLI - updates to changesets based on product chgs
  (bbuckingham@redhat.com)
- 855267 - CLI - updates to errata/package/repo based on product chgs
  (bbuckingham@redhat.com)
- 855267 - CLI add product label and id whereever product name is supported
  (bbuckingham@redhat.com)

* Fri Oct 19 2012 Miroslav Suchý <msuchy@redhat.com> 1.2.1-1
- gettext - fix malformed gettext stings in CLI code (inecas@redhat.com)
- Fix pylint katello.client.core.organization C0301 (inecas@redhat.com)
- default custom info for systems by org (komidore64@gmail.com)
- custom info rework (work it!) (komidore64@gmail.com)
- fix failing system tests (pchalupa@redhat.com)
- domains cli - fix for listing without --order or --search
  (tstrachota@redhat.com)
- cli - pylint fixes (tstrachota@redhat.com)
- manifests - Added delete manifest while in headpin mode (not enabled in
  katello) manifests - fixed 857949
  https://bugzilla.redhat.com/show_bug.cgi?id=857949 (thomasmckay@redhat.com)
- architectures - slice_dict extracted to utils (tstrachota@redhat.com)
- architectures - various cli fixes (tstrachota@redhat.com)
- architectures - cli unit tests (tomas.str@gmail.com)
- 866323 - do not print binary files to log (msuchy@redhat.com)
- Bumping package versions for 1.1. (lzap+git@redhat.com)
- remove old get ext imports (pchalupa@redhat.com)
- Architectures API fix (pajkycz@gmail.com)
- Added test_foreman_record to CLI utils to validate foreman resources
  (pajkycz@gmail.com)
- Added system tests for domains, config templates (pajkycz@gmail.com)
- CLI - rename show->info, destroy->delete (pajkycz@gmail.com)
- Foreman Config Templates improvements (pajkycz@gmail.com)
- Config templates CLI - print template kind (pajkycz@gmail.com)
- Foreman domains added to CLI client (pajkycz@gmail.com)
- Foreman's Config Templates added to CLI client. (pajkycz@gmail.com)
- architectures cli - show action renamed to info to keep naming consistency
  (tomas.str@gmail.com)
- cli - removed mutable types form default param values in Server class
  (tstrachota@redhat.com)
- architectures - CRUD CLI actions (tstrachota@redhat.com)
- cli - util functions for manipulating dicts and options
  (tstrachota@redhat.com)

* Fri Oct 12 2012 Lukas Zapletal <lzap+git@redhat.com> 1.1.10-1
- Merge pull request #846 from lzap/copyright-update
- updating copyrights
- katello-cli-headpin != katello-headpin-cli
- 864372 - CLI - some keys does not work in "shell"
- fixing 'ta' translations
- merge katello.cli translation from CFSE
- Merge pull request #808 from tstrachota/Bug_845198_locale_cannot_be_switched
- 845198 - fixed getlocale locale.getlocale was used with wrong parameter.
  LC_ALL is not allowed. See:
  http://docs.python.org/library/locale.html#locale.getlocale
- removing unused import in cli utils printer.py (komidore64@gmail.com)
- Merge pull request #803 from komidore64/org-list-fail
- Merge pull request #797 from xsuchy/pull-req-raise
- 863461 - Headpin Cli automation : Failure to list the org updated with
  special chars other than ascii chars (komidore64@gmail.com)
- 858960 - always set the utf-8 writer for stdout and stderr
- do not mask original error by raise in exception
- unify string "Couldn't find user role"
- unify string "Couldn't find user"
- unify string "Couldn't find template"
- 857576 - Fixing variable name in filter code
- 857576 - Fixed package code indentation

* Thu Sep 27 2012 Miroslav Suchý <msuchy@redhat.com> 1.1.9-1
- convert string to unicode (msuchy@redhat.com)
- 857576 - Added update filter test (davidd@scimedsolutions.com)
- 857576 - Package filter name can be edited by cli
  (davidd@scimedsolutions.com)
- move custom notes to separate file (msuchy@redhat.com)
- remove duplicate code (msuchy@redhat.com)
- W0104:228,8:GrepStrategy._print_header: Statement seems to have no effect
  (msuchy@redhat.com)
- W0212:135,8:VerboseStrategy._print_header: Access to a protected member
  _println of a client class E0602:135,8:VerboseStrategy._print_header:
  Undefined variable 'self' (msuchy@redhat.com)
- C0301:124,0: Line too long (129/120) C0301:971,0: Line too long (147/120)
  (msuchy@redhat.com)
- if using delimiter, then do not print padding spaces (msuchy@redhat.com)
- do not print first delimiter (msuchy@redhat.com)
- 801560 - correctly calculate length of asian characters (msuchy@redhat.com)
- 845995 - fixing typo (msuchy@redhat.com)
- refresh translations string for katello-cli (msuchy@redhat.com)
- some small python changes (komidore64@gmail.com)
- adding uuid arguments to system's custom info actions in the cli
  (komidore64@gmail.com)
- 858011 - pylint fixes (mmccune@redhat.com)
- removing a couple missed debugger statements (komidore64@gmail.com)
- CustomInfo for Systems (komidore64@gmail.com)
- object labels - fix cli tests broken during addition of object labels
  (bbuckingham@redhat.com)
- 797297 - fix typo (msuchy@redhat.com)
- 845995 - write error is systemgroup does not exist (msuchy@redhat.com)
- object-labels - adding CLI and API calls to support object labeling
  (mmccune@redhat.com)
- 836575 - fix encoding errors when reporting failure messages in CLI
  (inecas@redhat.com)
- Revert "regenerating localization strings for cli" (komidore64@gmail.com)
- regenerating localization strings for cli (komidore64@gmail.com)
- 820634 - Katello String Updates (komidore64@gmail.com)
- handle exception when katello server is down (msuchy@redhat.com)
- update cli source strings of localization (msuchy@redhat.com)
- object-label - organization - rename column cp_key to label
  (bbucking@dhcp231-20.rdu.redhat.com)
- cli - remove unused import (inecas@redhat.com)

* Wed Sep 12 2012 Ivan Necas <inecas@redhat.com> 1.1.8-1
- 837000 - [RFE] when updating sync plan by CLI, it resets the interval.
  (pajkycz@gmail.com)
- 809259 - activation key - cli permissions changes (continued)
  (bbuckingham@redhat.com)
- 809259 - activation key - cli permissions changes (bbuckingham@redhat.com)

* Wed Sep 12 2012 Miroslav Suchý <msuchy@redhat.com> 1.1.7-1
- Fixing provides/obsoletes bug (jomara@redhat.com)
- Removing extra configure code for headpin bin; adding provides to cli script
  for headpin (jomara@redhat.com)
- Fencing headpin CLI into katello cli. CLI will now load appropriate functions
  based on client.conf configuration. Katello cli now ships with headpin
  symlink (jomara@redhat.com)

* Thu Sep 06 2012 Ivan Necas <inecas@redhat.com> 1.1.6-1
- 835591 - usage limit is properly displayed in the list (lzap+git@redhat.com)
- make pylint happy on el6 (msuchy@redhat.com)
- cli - introducing %%{fastbuild} rpm macro use (lzap+git@redhat.com)
- 835591 - usage limit must be higher than 0 (lzap+git@redhat.com)
- cli - pull request review (lzap+git@redhat.com)
- cli refactoring - removing unused code (lzap+git@redhat.com)
- cli refactoring - update_dict_unless_none (lzap+git@redhat.com)
- cli - pull request review (lzap+git@redhat.com)
- fail to build if code contains pylint errors or warnings (msuchy@redhat.com)
- returning back docstring (msuchy@redhat.com)
- code cleanup - class Bytes is not used (msuchy@redhat.com)
- cli - removing unused global variable (lzap+git@redhat.com)
- 853995 - error handling for non-existing systems (lzap+git@redhat.com)
- since AsyncJob is instance of AsyncTask, there is no need for
  wait_for_async_job and we can use wait_for_async_task instead
  (msuchy@redhat.com)
- make _task attribute of instance instead of attribute of class
  (msuchy@redhat.com)
- Simplify AsyncJob by inheriting from AsyncTask (msuchy@redhat.com)
- create __str__() for AsyncJob (msuchy@redhat.com)
- cli - introducing debug log level env variable (lzap+git@redhat.com)
- 851142 - CLI: changeset update shows strange error (pajkycz@gmail.com)
- C0301: 26,0: Line too long (131/120) C0301:390,0: Line too long (135/120)
  (msuchy@redhat.com)
- removing reference to class that was removed (mmccune@redhat.com)
- removing reference to class that was removed (mmccune@redhat.com)
- waive W0221:177,4:KatelloCLI.error: Arguments number differs from overridden
  method (msuchy@redhat.com)
- waive R0904: 20,0:SystemGroupAPI: Too many public methods (21/20)
  (msuchy@redhat.com)
- waive R0904: 18,0:RepoAPI: Too many public methods (21/20 (msuchy@redhat.com)
- waive R0904: 19,0:SystemAPI: Too many public methods (29/20)
  (msuchy@redhat.com)
- waive W0702:478,4:get_term_width: No exception type(s) specified
  (msuchy@redhat.com)
- W0221:483,4:KatelloServer.PUT: Arguments number differs from overridden
  method (msuchy@redhat.com)
- W0221:480,4:KatelloServer.POST: Arguments number differs from overridden
  method (msuchy@redhat.com)
- W0221:474,4:KatelloServer.GET: Arguments number differs from overridden
  method (msuchy@redhat.com)
- W0702:364,8:KatelloServer._process_response: No exception type(s) specified
  (msuchy@redhat.com)
- waive R0904: 39,0:OptionParser: Too many public methods (39/20)
  (msuchy@redhat.com)
- W1201: 51,12:KatelloShell.history_file: Specify string format arguments as
  logging function parameters (msuchy@redhat.com)
- R0904: 30,0:KatelloShell: Too many public methods (21/20) (msuchy@redhat.com)
- W0201:279,12:Cmd.complete: Attribute 'completion_matches' defined outside
  __init__ (msuchy@redhat.com)
- W0703:186,15:Discovery.discover_repositories: Catching too general exception
  Exception (msuchy@redhat.com)
- R0904:170,0:ListAvailableVerbs: Too many public methods (22/20)
  (msuchy@redhat.com)
- R0904:183,0:UpdateContent: Too many public methods (21/20 (msuchy@redhat.com)
- W0611: 25,0: Unused import get_product (msuchy@redhat.com)
- R0904:272,0:Update: Too many public methods (26/20) (msuchy@redhat.com)
- remove false statement (msuchy@redhat.com)
- R0201: 35,4:EnvironmentAction.get_prior_id: Method could be a function
  (msuchy@redhat.com)
- W0622:503,12:Errata.run: Redefining built-in 'id' (msuchy@redhat.com)
- W0622:460,12:Packages.run: Redefining built-in 'id' (msuchy@redhat.com)
- C0301:331,0: Line too long (122/120) C0301:407,0: Line too long (122/120)
  C0301:409,0: Line too long (122/120) C0301:411,0: Line too long (145/120)
  C0301:413,0: Line too long (126/120) C0301:415,0: Line too long (126/120)
  C0301:417,0: Line too long (124/120) C0301:484,0: Line too long (124/120)
  (msuchy@redhat.com)
- R0201:233,4:ShowSubscriptions.convert_timestamp: Method could be a function
  R0201:239,4:ShowSubscriptions.extract_sla_from_product: Method could be a
  function (msuchy@redhat.com)
- R0201: 53,4:DateTimeFormatter.local_timezone: Method could be a function
  (msuchy@redhat.com)
- W0621: 42,35:DateTimeFormatter.build_datetime: Redefining name 'time' from
  outer scope (line 18) (msuchy@redhat.com)
- W0621: 39,28:DateTimeFormatter.contains_zone: Redefining name 'time' from
  outer scope (line 18) (msuchy@redhat.com)
- W0621: 36,25:DateTimeFormatter.date_valid: Redefining name 'time' from outer
  scope (line 18) (msuchy@redhat.com)
- W0621: 33,25:DateTimeFormatter.time_valid: Redefining name 'time' from outer
  scope (line 18) (msuchy@redhat.com)
- W0232: 24,0:DateTimeFormatter: Class has no __init__ method
  (msuchy@redhat.com)
- R0201: 35,4:ActivationKeyAction.get_template_id: Method could be a function
  (msuchy@redhat.com)
- C0301: 62,0: Line too long (126/120) C0301:233,0: Line too long (144/120)
  (msuchy@redhat.com)
- waive Method could be a function (msuchy@redhat.com)
- waive unused arguments (msuchy@redhat.com)
- W0702:387,12:BaseAction.main: No exception type(s) specified
  (msuchy@redhat.com)
- R0201:342,4:BaseAction.load_saved_options: Method could be a function
  (msuchy@redhat.com)
- W0702:278,8:Command._extract_command: No exception type(s) specified
  (msuchy@redhat.com)
- R0201:257,4:Command.__build_command_usage_lines: Method could be a function
  (msuchy@redhat.com)
- R0201:214,4:Action.__process_option_errors: Method could be a function
  (msuchy@redhat.com)
- waive unused arguments (msuchy@redhat.com)
- C0301:333,0: Line too long (179/120) C0301:335,0: Line too long (172/120)
  (msuchy@redhat.com)
- W0611: 19,0: Unused import Command (msuchy@redhat.com)
- simplify code (msuchy@redhat.com)
- R0201: 86,4:Status.__sortedStatuses: Method could be a function R0201:
  93,4:Status.__buildOverallStatusDetail: Method could be a function R0201:
  99,4:Status.__buildServiceStatusDetail: Method could be a function
  (msuchy@redhat.com)
- waive W0612: 70,12:Status.__returnCode: Unused variable 'serviceName'
  (msuchy@redhat.com)
- R0201: 39,4:SyncPlanAction.parse_datetime: Method could be a function
  (msuchy@redhat.com)
- C0301:115,0: Line too long (127/120) C0301:118,0: Line too long (147/120)
  C0301:150,0: Line too long (127/120) (msuchy@redhat.com)
- R0201:289,4:Promote.create_cs_name: Method could be a function
  (msuchy@redhat.com)
- rename isMarketingProduct to isNotMarketingProduct to avoid confusion of
  future generations (msuchy@redhat.com)
- W0702:159,16:List.run.isMarketingProduct: No exception type(s) specified
  (msuchy@redhat.com)
- W0622:132,8:List.run: Redefining built-in 'all' (msuchy@redhat.com)
- R0201: 58,4:SingleProductAction.set_product_select_options: Method could be a
  function R0201: 64,4:SingleProductAction.check_product_select_options: Method
  could be a function (msuchy@redhat.com)
- C0301: 29,0: Line too long (135/120) C0301:228,0: Line too long (134/120)
  C0301:248,0: Line too long (124/120) C0301:308,0: Line too long (121/120)
  C0301:312,0: Line too long (128/120) C0301:314,0: Line too long (158/120)
  (msuchy@redhat.com)
- W0201:354,8:Update.resetParameters: Attribute 'items' defined outside
  __init__ (msuchy@redhat.com)
- W0201:291,8:Update.store_from_product: Attribute 'current_product' defined
  outside __init__ (msuchy@redhat.com)
- R0201:418,4:Update.productNamesToIds: Method could be a function
  R0201:429,4:Update.repoNamesToIds: Method could be a function
  (msuchy@redhat.com)
- waive unused arguments (msuchy@redhat.com)
- R0201:223,4:Export.open_file: Method could be a function (msuchy@redhat.com)
- W0702:211,8:Export.run: No exception type(s) specified (msuchy@redhat.com)
- W0622:204,8:Export.run: Redefining built-in 'format' (msuchy@redhat.com)
- R0201:177,4:Import.open_file: Method could be a function (msuchy@redhat.com)
- W0702:167,8:Import.run: No exception type(s) specified (msuchy@redhat.com)
- R0201:125,4:Info._build_nvrea: Method could be a function (msuchy@redhat.com)
- R0201: 39,4:TemplateAction.get_parent_id: Method could be a function
  (msuchy@redhat.com)
- C0301:171,0: Line too long (129/120) C0301:193,0: Line too long (123/120)
  C0301:215,0: Line too long (133/120) C0301:311,0: Line too long (137/120)
  C0301:313,0: Line too long (155/120) C0301:314,0: Line too long (123/120)
  C0301:317,0: Line too long (124/120) C0301:319,0: Line too long (146/120)
  C0301:320,0: Line too long (152/120) C0301:323,0: Line too long (123/120)
  C0301:325,0: Line too long (132/120) C0301:327,0: Line too long (141/120)
  C0301:329,0: Line too long (147/120) C0301:400,0: Line too long (134/120)
  (msuchy@redhat.com)
- correctly use pylint: disable (msuchy@redhat.com)
- 746765 - systems can be referenced by uuid (lzap+git@redhat.com)

* Fri Aug 31 2012 Miroslav Suchý <msuchy@redhat.com> 1.1.5-1
- code style fixes (msuchy@redhat.com)
- 847858 - only remove act keys when resource not found error
  (thomasmckay@redhat.com)

* Wed Aug 29 2012 Ivan Necas <inecas@redhat.com> 1.1.4-1
- evironment is now stored to environment variable instead env
  (msuchy@redhat.com)
- fix unit tests (msuchy@redhat.com)
- add to path correct search location (msuchy@redhat.com)
- package unit tests (msuchy@redhat.com)
- Available subscriptions on systems page now allow filtering matching what is
  available in subscription-manager-gui (thomasmckay@redhat.com)
- waive pylint R0201: 43,4:KatelloShell.history_file: Method could be a
  function (msuchy@redhat.com)
- Revert "declare method as function" (msuchy@redhat.com)
- waive pylint R0201: 30,4:KatelloAPI.server: Method could be a function
  (msuchy@redhat.com)
- Revert "R0201: 30,4:KatelloAPI.server: Method could be a function"
  (msuchy@redhat.com)
- 845198 - do not fail with 'C' locale (msuchy@redhat.com)
- 845198 - set locale even in usage.py to allow building (msuchy@redhat.com)
- 845198 - receive translation from gettext as unicode (msuchy@redhat.com)
- fixing various unit tests from content deletion and param unification
  (mmccune@redhat.com)
- stylecheck fixes (msuchy@redhat.com)
- there is no option -environment in this action (msuchy@redhat.com)
- 848038 - installing localisation files for cli (tstrachota@redhat.com)
- 850790 - Content promotion from CLI no longer works (lzap+git@redhat.com)
- 798679 - Read correct argument (msuchy@redhat.com)
- fix incorrect argument (msuchy@redhat.com)
- 798679 - be consistent with --environment option help (msuchy@redhat.com)
- 798679 - be consistent with --org option help (msuchy@redhat.com)
- 798679 - remove duplicate code handling --product option (msuchy@redhat.com)
- 798679 - be consistent with --product option help (msuchy@redhat.com)
- 846321: Support creating permissions for all tags from the API and the cli
  (bkearney@redhat.com)
- 845995: Add local and server side checks for passing in bad group names and
  ids (bkearney@redhat.com)
- 771186 - katello ak info now shows aks (lzap+git@redhat.com)
- 845198 - always use utf-8 as output encoding (tomas.str@gmail.com)
- 845198 - enable setting locale via LC_ALL in cli (tomas.str@gmail.com)

* Thu Aug 23 2012 Mike McCune <mmccune@redhat.com> 1.1.3-1
- 850935 - katello-cli-common should own only /etc/katello and not its content
  (msuchy@redhat.com)
- 795520 - modifying manual page (lzap+git@redhat.com)
- 795520 - removing unused variable (lzap+git@redhat.com)
- 795520 - adding support of noheading cli option (lzap+git@redhat.com)
- Merge pull request #436 from omaciel/userlocale (mmccune@gmail.com)
- Validation of locale during update handled by model. (ogmaciel@gnome.org)
- Allow user to update his/her own localevia cli. Also, output the default
  locale when using the info parameter. (ogmaciel@gnome.org)
- Added --default_locale to CLI for user creation. (ogmaciel@gnome.org)
- Fixed some merge conflicts (paji@redhat.com)
- content deletion - proper deletion support in the CLI (mmccune@redhat.com)
- content deletion - adding back in the CLI promote and apply
  (mmccune@redhat.com)
- content deletion - removing hard coded type (mmccune@redhat.com)
- content deletion - adding CLI actions (mmccune@redhat.com)

* Thu Aug 16 2012 Lukas Zapletal <lzap+git@redhat.com> 1.1.2-1
- 822926 - katello-cli-common now owns config dir
- 822926 - fixing incorrect license in a header

* Sat Aug 11 2012 Miroslav Suchý <msuchy@redhat.com> 1.1.1-1
- cli docs - removed version from config (tomas.str@gmail.com)
- cli - Config inicialization moved to functions It was causing problems in
  test when we tried to init it at include time. Unused Config inits were
  removed. (tstrachota@redhat.com)
- cli doc - added docs for cli generator (tstrachota@redhat.com)
- cli doc - first version of sphinx documentation (tstrachota@redhat.com)
- buildroot and %%clean section is not needed (msuchy@redhat.com)
- Bumping package versions for 1.1. (msuchy@redhat.com)

* Tue Jul 31 2012 Miroslav Suchý <msuchy@redhat.com> 1.0.1-1
- bump up version to 1.0 (msuchy@redhat.com)
- update copyright years (msuchy@redhat.com)
- point Source0 to fedorahosted.org where tar.gz are stored (msuchy@redhat.com)

* Wed Jul 25 2012 Miroslav Suchý <msuchy@redhat.com> 0.2.45-1
- 840531 - Fixes issue with inability to individually promote packages attached
  to a system template or changeset that have more than a single dash in the
  name. (ehelms@redhat.com)
- 817845 - updating katello man page entry (adprice@redhat.com)

* Mon Jul 23 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.44-1
- system groups - API accepts max_systems and CLI unit tests
- system groups - wrong variable name in error message
- system groups - removing local modifications not intended for upstream
- group copy cli and API first pass

* Mon Jul 16 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.43-1
- 798323 - remove double setting of UTF decoder
- system groups - removing the 'locked' feature from system groups UI/API/CLI
- system groups - update errata list cli based on pull request feedback
- system groups - api/cli - add ability to list errata by group
- cli - fix for url options not allowing file:// and ftp://

* Mon Jul 02 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.42-1
- system groups - cli - fix broken test
- system groups - cli - creating a group should default max systems to
  unlimited
- system groups - cli - add description to the AsyncJob
- system groups - cli - split history in to 2 actions per review feedback
- system groups - api/cli to support errata install
- system groups - remove unused code from package action CLI
- system groups - api/cli to support package and package group actions

* Mon Jun 25 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.41-1
- ulimit - brad's review
- BZ 825262: support for moving systems between environments from CLI
- ulimit - fixing cli makefile for unit tests
- ulimit - backend api and cli
- system groups - cli/api - provide user option to delete systems when deleting
  group
- cli - updated makefile and readme to mirror the latest changes in cli
  unittests.

* Mon Jun 18 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.40-1
- Updates for broken cli unit tests that were a result of re-factoring work
  previously done.
- system groups - api - include total system count in system group info
- system group cli - removed excess lines
- cli - fix for printing version on -v option
- cli unit tests - tests splitted into packages and modules
- 822484 - cli - sync_plan list traceback
- cli - pep8 fixes
- cli - action base class renamed
- cli - usage script modified to use command container
- cli - auth methods extracted form server class
- cli - fixed shell completion and line preprocessing
- cli - katello cli turned to new-style command
- cli - unittests fixed after introduction of new option types
- cli - allow to use only user config file
- 818726 - updated i18n translations
- cli - new option types - url and list
- 818726 - update to both ui and cli and zanata pushed

* Fri Jun 01 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.39-1
- system grops - a few fixes for history cli
- cli - None check in date_formatter + enabled system test for deleting filters
- system groups - adding group history to cli
- cli - adding log file location to traceback error
- 821644 - cli admin crl_regen command - unit and system test
- 822926 - katello-cli package fedora review - fix

* Fri May 25 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.38-1
- 822926 - katello-cli package fedora review
- Fixed typo s/fing/find. Fixes BZ #824749.
- system groups - Updates for help text around options that take lists and
  command naming for adding groups to a system.
- 795525 - renaming cli column name 'subscriptions'
- system groups - Updates the system groups CLI work to be consistent with re-
  factoring work.
- system groups - merge conflict
- system groups - Updates to not require max_systems on creation in CLI.
- Two minor tweaks to output strings for removing systems from a system group.
- system groups - Adds the maximum systems paramter for CLI create/update.
- system groups - Cleans up CLI code to fit re-factoring changes from master.
- system groups - Adds CLI support for add/remove of a system group from an
  activation key.
- system groups - Clean up CLI code around adding systems to a system group
- system group - Adds CLI/API support for adding and removing system groups
  from a system
- system groups - Adds support for removing systems from a system group in CLI.
- system groups - Adds support for adding systems to a system group in the CLI
- Adds system group basic update support for the CLI
- system group - Adds system group delete to CLI.
- system group - Adds system group creation support to CLI.
- system group - Adds support for locking and unlocking a system group in the
  CLI
- system groups - Adds CLI support for listing systems in a system group.
- system groups - Adds ability to view info of single system group from CLI.
- system-groups - Adds CLI system group basics and calls to list system groups
  for a given organization.

* Thu May 24 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.37-1
- 824069 - adding new parameter --all to cli product list
- cli - workaround for error when action was not found This commit fixes error
  "object has no attribute 'parser'" appearing after attempt to call a non-
  existing action. The error is gone but classes Command and KatelloCLI need
  more cleanup. There's redundant code and they touch each other's
  responsibility.
- cli - fix for missing section 'options' client.conf Some versions of
  OptionParser throw error when you try to iterate items from non-existing
  section.
- cli validator - complete unit tests
- cli - validator and parser moved from class to local variables This helps the
  code to be more testable.
- cli - fix for wrong param validation in system register
- cli - CLITestCase divided into two classes
- cli - unit tests for required options simplified
- cli - methods for validation extracted from cli Action

* Fri May 18 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.36-1
- rpm review - katello-cli review preparation

* Fri May 18 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.35-1
- cli registration regression with aks

* Thu May 17 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.34-1
- cli_man - katello(1) man page and generator
- Changing wording for hypervisor deletion record delete
- 812891 - Adding hypervisor record deletion to katello cli
- product status cli - fix for key error Formatting moved to printer that
  checks whether the key exist prior to printing it.

* Thu May 10 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.33-1
- cli - pep8 fixes - code reidentation - trailing spaces removal - unused
  imports removed
- cli - fixes in unit tests
- cli - removal of redundant code
- task list cli - print part refactored Duplicit lines removed and changed to
  use new style printer.
- cli - new method for testing success of a record creation
- cli - api util methods changed to raise exceptions instead of returning None
  when a record was not found. This allows us to remove the ubiquitous checks
  for None value from action bodies.
- systems cli - actions use new api util method get_system
- systems cli - method get_environment moved out from system api class
- Added cli tests for ldap_roles
- Added mocks for ldap_group api call
- 808172 - Added code to show version information for katello cli
- systems - cli for listing systems for a pool_id

* Fri Apr 27 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.32-1
- Fixed addColumn to match new name
- Fixing various LDAP issues from the last pull request
- Loading group roles from ldap
- 767925 - search packages command in CLI/API

* Tue Apr 24 2012 Petr Chalupa <pchalupa@redhat.com> 0.2.31-1
- katello-cli, katello - setting default environment for user

* Thu Apr 19 2012 Tomas Strachota <tstrachota@redhat.com> 0.2.30-1
- cli - fixed wrong formatters used for product and repo last sync time

* Thu Apr 19 2012 Tomas Strachota <tstrachota@redhat.com> 0.2.29-1
- periodic-build
* Wed Apr 18 2012 Petr Chalupa <pchalupa@redhat.com> 0.2.28-1
- 812842 - complete removal of skipping None values in verbose print strategy
- 741595 - uebercert POST/GET/DELETE - either support or delete the calls from
  CLI

* Tue Apr 17 2012 Tomas Strachota <tstrachota@redhat.com> 0.2.27-1
- 812842 - fix for cli printer skipping values that are evaluated as False
- 798918 - Headpin cli unregister doesn't have environment option

* Fri Apr 13 2012 Tomas Strachota <tstrachota@redhat.com> 0.2.26-1
- cli - documentation strings for printer
- cli - output formatters in printer
- cli - fix for method set_output_mode removed from Printer
- cli - printer refactored to enable more output modes
- cli - printer class moved out from utils.py into separate file

* Thu Apr 12 2012 Ivan Necas <inecas@redhat.com> 0.2.25-1
- cp-releasever - release as a scalar value in API system json
- 769302 - CLI `system register` needs enhancement

* Wed Apr 11 2012 Petr Chalupa <pchalupa@redhat.com> 0.2.24-1
- 713153 - RFE: include IP information in consumers/systems related API calls.
- 768243 - Error msg needs to be improved

* Tue Apr 10 2012 Tomas Strachota <tstrachota@redhat.com> 0.2.23-1
- slas - all cli options --service_level renamed to --servicelevel

* Fri Apr 06 2012 Tomas Strachota <tstrachota@redhat.com> 0.2.22-1
- slas - field for SLA in hash export of consumer renamed We used service_level
  but subscription-manager requires serviceLevel and checks for it's presence.
* Wed Apr 04 2012 Petr Chalupa <pchalupa@redhat.com> 0.2.21-1
- 798649 - RFE - Better listing of products and repos

* Mon Apr 02 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.20-1
- cleanup - removing unused imports and variables
- 744199 - cli now reports all errors to stderr

* Tue Mar 27 2012 Ivan Necas <inecas@redhat.com> 0.2.18-1
- periodic-build

* Mon Mar 26 2012 Ivan Necas <inecas@redhat.com> 0.2.16-1
- periodic build

* Mon Mar 19 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.14-1
- 803441 - fix cli unit test for org subscriptions

* Thu Mar 15 2012 Ivan Necas <inecas@redhat.com> 0.2.13-1
- priodic build

* Tue Mar 13 2012 Ivan Necas <inecas@redhat.com> 0.2.12-1
- periodic build

* Mon Mar 12 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.10-1
- 801786 - putting client.conf back to the RPM

* Fri Mar 09 2012 Mike McCune <mmccune@redhat.com> 0.2.9-1
- periodic rebuild
* Fri Mar 02 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.3-1
- 798264 - Katello debug collects certificate password files and some certs

* Mon Feb 27 2012 Lukas Zapletal <lzap+git@redhat.com> 0.2.2-1
- Pull in the latest translations

* Wed Feb 22 2012 Mike McCune <mmccune@redhat.com> 0.2.1-1
- version bump

* Wed Feb 22 2012 Ivan Necas <inecas@redhat.com> 0.1.57-1
- periodic build
* Fri Feb 17 2012 Brad Buckingham <bbuckingham@redhat.com> 0.1.56-1
- 794782: Add PyXML to the cli dependencies (bkearney@redhat.com)

* Tue Feb 07 2012 Ivan Necas <inecas@redhat.com> 0.1.53-1
- 768254 - scope products API by organization (inecas@redhat.com)

* Mon Feb 06 2012 Ivan Necas <inecas@redhat.com> 0.1.51-1
- periodic build

* Mon Jan 30 2012 Lukas Zapletal <lzap+git@redhat.com> 0.1.47-1
- repo cli - option --environment removed from 'repo delete'

* Sat Jan 28 2012 Martin Bačovský <mbacovsk@redhat.com> 0.1.46-1
- Fixed failing tests (mbacovsk@redhat.com)

* Thu Jan 26 2012 Shannon Hughes <shughes@redhat.com> 0.1.44-1
- 783513 - CLI BRANDING: Locker -> Library (mbacovsk@redhat.com)

* Tue Jan 24 2012 Bryan Kearney <bkearney@redhat.com> 0.1.42-1
- 754856: Define the userdir only in the Config module (bkearney@redhat.com)

* Tue Jan 24 2012 Martin Bačovský <mbacovsk@redhat.com> 0.1.41-1
- 782775 - Unify unsubscription in RHSM and Katello CLI (mbacovsk@redhat.com)
- 772183 - ProvidedProducts: displays too much of information for RH Pools (mbacovsk@redhat.com)
- 773521 - Help text should include "entitlement ID" instead of "pool id" (mbacovsk@redhat.com)
- Added require_one_of_options checker to CLI Action (mbacovsk@redhat.com)
- Fixed exit codes in 'system subscriptions' (CLI) (mbacovsk@redhat.com)
- 767470 - Unable to fetch subscription serial numbers from cli (mbacovsk@redhat.com)
- dists - adding required string to the repo_id param (lzap+git@redhat.com)

* Thu Jan 19 2012 Lukas Zapletal <lzap+git@redhat.com> 0.1.39-1
- perms - moving /errata/id under /repositories API
- perms - moving /packages/id under /repositories API

* Thu Jan 19 2012 Ivan Necas <inecas@redhat.com> 0.1.38-1
- periodic build

* Wed Jan 18 2012 Ivan Necas <inecas@redhat.com> 0.1.37-1
- gpg cli support

* Fri Jan 06 2012 Ivan Necas <inecas@redhat.com> 0.1.34-1
- 771911 - CLI - update success message after system update (inecas@redhat.com)

* Thu Dec 22 2011 Ivan Necas <inecas@redhat.com> 0.1.31-1
- periodic rebuild

* Wed Dec 14 2011 Ivan Necas <inecas@redhat.com> 0.1.27-1
- Fix bug on cli repo info for disabled repository (inecas@redhat.com)

* Wed Dec 14 2011 Shannon Hughes <shughes@redhat.com> 0.1.25-1
- system engine build

* Thu Dec 08 2011 Mike McCune <mmccune@redhat.com> 0.1.23-2
- periodic rebuild
* Thu Dec 08 2011 Mike McCune <mmccune@redhat.com>
- periodic rebuild

* Tue Dec 06 2011 Shannon Hughes <shughes@redhat.com> 0.1.22-1
- 758447: Allow the prompt to be customized via the config file
  (bkearney@redhat.com)

* Fri Dec 02 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.20-1
- ueber - fixing cli unit tests
- generate_uebercert -> ubercert in the cli

* Tue Nov 29 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.18-1
- adding template to the system info cli call
- show activation keys in the cli system info

* Mon Nov 28 2011 Tomas Strachota <tstrachota@redhat.com> 0.1.17-1
- cli - fix for spinner being trapped in a loop (tstrachota@redhat.com)
- cli unit tests - cancel product synchronization (tstrachota@redhat.com)
- cli unit tests - option test for SingleProductAction (tstrachota@redhat.com)
- cli - whitespace removal (tstrachota@redhat.com)
- cli unit tests - tests around provider actions (tstrachota@redhat.com)
- sync cli - cancel current provider sync (tstrachota@redhat.com)
- cli - refactoring in provider-centric actions (tstrachota@redhat.com)

* Mon Nov 28 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.16-1
- tdl validations - backend and cli

* Fri Nov 25 2011 Tomas Strachota <tstrachota@redhat.com> 0.1.15-1
- sync cli - repo status fixed according to changes in async taks format
  (tstrachota@redhat.com)
- sync cli - cancelling current product synchronization (tstrachota@redhat.com)
- cli - actions around single products refactored (tstrachota@redhat.com)
- sync cli - actions around single repositories refactored
  (tstrachota@redhat.com)
- sync cli - cancelling current repo sync (tstrachota@redhat.com)
- provider cli - removed needless option '--type' (tstrachota@redhat.com)
- repo blacklist - cli unit tests for repo list (tstrachota@redhat.com)
- Revert "repo blacklist - cli unit tests for repo list"
  (tstrachota@redhat.com)
- repo blacklist - cli unit tests for repo list (tstrachota@redhat.com)
- bug - cli was not working when locale was not set (lzap+git@redhat.com)
- repo blacklist - listing disabled repos in the cli (tstrachota@redhat.com)
- repo blacklist - cli for enabling/disabling repos (tstrachota@redhat.com)
- bug - race condition in the cli spinner (lzap+git@redhat.com)
- template export - checking output format moved to option parser
  (tstrachota@redhat.com)
- template export - disabled exporting templates from Locker envs
  (tstrachota@redhat.com)

* Tue Nov 15 2011 Shannon Hughes <shughes@redhat.com> 0.1.12-1
- Merge branch 'master' into password_reset (bbuckingham@redhat.com)
- cli - removed unused 'flag' argument from a method 'Command#require_option'
  (tstrachota@redhat.com)
- cli - parameter flag determined automatically for required arguments It is no
  longer necessary to pass both expected destination and flag string to the
  'require_option' method when those two are different. (tstrachota@redhat.com)
- Merge branch 'master' into password_reset (bbuckingham@redhat.com)
- Merge branch 'master' into password_reset (bbuckingham@redhat.com)
- Merge branch 'master' into password_reset (bbuckingham@redhat.com)
- cli - add email address to 'user' as a required attribute
  (bbuckingham@redhat.com)

* Thu Nov 10 2011 Shannon Hughes <shughes@redhat.com> 0.1.11-1
- moving system tests into /scripts (lzap+git@redhat.com)
- cli - code reindentation & pep8 fixes (tstrachota@redhat.com)
- repo cli - fixed failure in repo info caused by api not returning all
  information (tstrachota@redhat.com)
- Merge branch 'repo-remodel' of ssh://git.fedorahosted.org/git/katello into
  repo-remodel (paji@redhat.com)
- Fixed the bash script to retrieve the pulp id correctly (paji@redhat.com)
- changeset cli - fix for listing repo names in changeset info
  (tstrachota@redhat.com)
- changeset system tests - removed repo dependency +calling changeset info with
  on changeset with content (tstrachota@redhat.com)
- Merge branch 'master' into repo-remodel (paji@redhat.com)
- removing unnecessary sleep from test (lzap+git@redhat.com)
- bug - error message when registering a system (lzap+git@redhat.com)
- system tests - testing failure of package group listing
  (tstrachota@redhat.com)
- system tests - support for using pulp_repo_id (tstrachota@redhat.com)
- up-to-date fake manifest (lzap+git@redhat.com)
- bug - cli was not reporting nonexisting ak (lzap+git@redhat.com)
- cli tests - fixed wrong mocking of 'save_report' (tstrachota@redhat.com)
- cli tests - test for ping (tstrachota@redhat.com)
- cli ping - return code reflects status of subsystems (tstrachota@redhat.com)
- cli tests - using deepcopy instead of copy in utils for mocking
  (tstrachota@redhat.com)
- cli - better description for 'product promote' (tstrachota@redhat.com)
- cli - support for multiline description of actions (tstrachota@redhat.com)
- cli - support for multiline description of commands (tstrachota@redhat.com)
- 749570 - showing pool id along with subscriptions (lzap+git@redhat.com)
- fixing formatting (lzap+git@redhat.com)
- fixing cli unit tests - one more (lzap+git@redhat.com)
- fixing cli unit tests (lzap+git@redhat.com)
- system tests - changed generating random hash (tstrachota@redhat.com)
- adding new parameter --nodisc for product creation (lzap+git@redhat.com)
- distros - adding cli portion for adding/removing distros
  (lzap+git@redhat.com)
- distros - adding family, variant, version in CLI (lzap+git@redhat.com)
- fxiing merge conflict (jsherril@redhat.com)
- Merge branch 'master' into errata_filter (bbuckingham@redhat.com)
- cli test for 'org subscriptions' command (dmitri@redhat.com)
- subscription start/end dates are now being coverted into human-readable
  format (dmitri@redhat.com)
- sla information is now being added to subscriptions (dmitri@redhat.com)
- added support for listing of subscriptions for an organization
  (dmitri@redhat.com)
- tdl-export - expose template export in the CLI (inecas@redhat.com)
- Break up the cli spec file into a common and katello piece
  (bkearney@redhat.com)
- nvrea-optional - system test for nvrea support (inecas@redhat.com)
- Merge branch 'reports' (dmitri@redhat.com)
- sys tests - enabled org delete test in provider import testsuite
  (tstrachota@redhat.com)
- Merge branch 'master' into errata_filter (bbuckingham@redhat.com)
- improving python code style (lzap+git@redhat.com)
- cli-akeys-pools - show pools in activation key details (inecas@redhat.com)
- cli-akeys-pools - remove subscriptions from a activation kay
  (inecas@redhat.com)
- cli-akeys-pools - add subscription to a key through CLI (inecas@redhat.com)
- merge conflict (jsherril@redhat.com)
- add/remove package updates for cli system test for filters
  (dmitri@redhat.com)
- tests for cli for add/remove package to/from filter (dmitri@redhat.com)
- cli tests for filters (dmitri@redhat.com)
- added support for updating of package lists of filters (dmitri@redhat.com)
- merge conflict (jsherril@redhat.com)
- pools - adding multi entitlement flag to the list (cli) (lzap+git@redhat.com)
- pools - making use of system.available_pools_full (lzap+git@redhat.com)
- pools - listing of available pools (lzap+git@redhat.com)
- added filter-related tests to cli-tests (dmitri@redhat.com)
- added tests for filter operations in katello cli (dmitri@redhat.com)
- more product-filter association tests for cli (dmitri@redhat.com)
- added product-filter association tests for cli (dmitri@redhat.com)
- errata-filters - filter all errata for a product (inecas@redhat.com)
- merge conflict (jsherril@redhat.com)
- fogot to commit some filter-related files (for cli) (dmitri@redhat.com)
- added support for listing/adding/removing filters to/from products from
  katello cli (dmitri@redhat.com)
- added support for filter create/list/show/delete operations in katello cli
  (dmitri@redhat.com)
- errata-filters - API and CLI support for filtering on severity
  (inecas@redhat.com)
- errata-filters - API and CLI restrict filtering errata on an environment
  (inecas@redhat.com)
- errata-filters - API and CLI allow errata filtering on multiple repos
  (inecas@redhat.com)
- errata-filters - API and CLI support for filtering errata by type
  (inecas@redhat.com)
- errata-filters - cli support for filtering errata by type (inecas@redhat.com)
- cli - disabled two pylint false alarms (tstrachota@redhat.com)
- Merge branch 'master' of ssh://git.fedorahosted.org/git/katello
  (bkearney@redhat.com)
- pulp-repo-secured - system test for chekcing the seruted repo
  (inecas@redhat.com)
- Merge branch 'master' of ssh://git.fedorahosted.org/git/katello
  (bkearney@redhat.com)
- Small refactoring (inecas@redhat.com)
- New cli strings pushed (bkearney@redhat.com)
- repo delete - cli unit test (tstrachota@redhat.com)
- added more cli report tests (dmitri@redhat.com)
- Fix index error when printing cli table (inecas@redhat.com)
- recreated cli report tests (dmitri@redhat.com)
- re-created reports functionality after botched merge (dmitri@redhat.com)
- 743883 - propper testing on provided url (inecas@redhat.com)
- repo delete - enabled in system tests (tstrachota@redhat.com)
- repo cli - refactored way of getting repos (tstrachota@redhat.com)
- repo delete - cli for deleting single repos (tstrachota@redhat.com)
- 741274 - correct displaying of unicode values in info (inecas@redhat.com)
- 741274 - correct displaying of unicode values in listings (inecas@redhat.com)
- system tests - added option for disabling the base cleanup test -c or
  --nocleanup (tstrachota@redhat.com)
- cli unit tests - test for product delete (tstrachota@redhat.com)
- system tests - enabled removing products in cleanup test
  (tstrachota@redhat.com)
- products - cli for removing products (tstrachota@redhat.com)
- fix for katello-reset-dbs - pgsql support for initdb - typo
  (lzap+git@redhat.com)
- sms - list of certificates in the cli (lzap+git@redhat.com)
- sms - refactoring subscription -> subscriptions path (lzap+git@redhat.com)
- sms - moving subscriptions list action into the backend (lzap+git@redhat.com)
- sms - moving unsubscribe action into the backend (lzap+git@redhat.com)
- 723308 - show names instead of ids in cli environment info
  (inecas@redhat.com)
- disabling one system cli test due to bug (lzap+git@redhat.com)
- sms - subscriptions cli command (lzap+git@redhat.com)
- templates - removed old way of promoting templates directly
  (tstrachota@redhat.com)
- cli unit tests - added exit code tests for template update
  (tstrachota@redhat.com)
- cli unit tests - tests for template update (tstrachota@redhat.com)
- packagegroups - parameter 'repoid' changed to 'repo_id' to keep the cli
  consistent (tstrachota@redhat.com)
- system tests - fix for problem with dependencies test for templates require
  packagegroups (tstrachota@redhat.com)
- packagegroups cli - removed pprint form command 'info'
  (tstrachota@redhat.com)
- system tests - update of parameters for templat cli in changeset test
  (tstrachota@redhat.com)
- packagegroups - fixes in unit tests Fixes for testing api that returns arrays
  instead of hashes. (tstrachota@redhat.com)
- packagegroups - cli changed to work with array returned from api instead of
  hashes that were returned formerly (tstrachota@redhat.com)
- templates - system tests for updates (tstrachota@redhat.com)
- templates cli - update command exits when product was not found
  (tstrachota@redhat.com)
- package groups - groups and group categories returned in an array instead of
  in a hash (tstrachota@redhat.com)
- cli - removed deprecated '<>' (tstrachota@redhat.com)
- templates cli - removed old route for content update (tstrachota@redhat.com)
- templates cli - command 'update_content' removed (tstrachota@redhat.com)
- templates cli - package groups and group categories added to update
  (tstrachota@redhat.com)
- templates cli - content update using new api (tstrachota@redhat.com)
- providing final system test fix for RH autocreation (lzap+git@redhat.com)
- fixing provider import after providers branch merge (lzap+git@redhat.com)
- correcting system test for default RH provider (lzap+git@redhat.com)
- sms - improving default value for quantity (lzap+git@redhat.com)
- cli - removed default value from get_option It was colliding with default
  value from optparse and as a result the default value from get_option was
  never used. (tstrachota@redhat.com)
- sms - cli system subscribe command (lzap+git@redhat.com)
- sms - remove a subscription from a machine (lzap+git@redhat.com)
- updated bin/katello to show correct names for uebercert-related commands
  (dmitri@redhat.com)
- Revert "BZ 741357: fixed a spelling mistake in katello-jobs.init"
  (dmitri@redhat.com)
- BZ 741357: fixed a spelling mistake in katello-jobs.init (dmitri@redhat.com)
- added cli support for generation/retrieval of uebercerts (dmitri@redhat.com)
- templates cli - fix for printing None instead of Locker in template list
  (tstrachota@redhat.com)
- system tests - new tests for templates and changesets (tstrachota@redhat.com)
- templates api - fix for getting template by name (tstrachota@redhat.com)
- cli unit tests - updated template package test data - added nvre information
  - removed errata (tstrachota@redhat.com)
- templates cli - showing nvre in tepmlate info (tstrachota@redhat.com)
- templates cli - removed errata from template info (tstrachota@redhat.com)
- changesets - cli support for adding template to changesets
  (tstrachota@redhat.com)
- templates cli - removed errata from updates (tstrachota@redhat.com)
- system tests - added function for checking katello jobs
  (tstrachota@redhat.com)
- system tests - added test_success and test_failure methods
  (tstrachota@redhat.com)
- system templates - refactoring - removed ordering by numbers in filename -
  added ability to define required test suites to run them prior the current
  test suite - added function for printing a suite header, headers must be
  printed in the test files now (tstrachota@redhat.com)
- packagegroup-templates - fix failing cli unit tests (inecas@redhat.com)
- packagegroups-templates - show comps in template info (inecas@redhat.com)
- 732007 - enhanced error message in CLI (inecas@redhat.com)
- Merge branch 'master' of ssh://git.fedorahosted.org/git/katello
  (dmitri@redhat.com)
- 733266 - new option type bool to handle True/False options
  (inecas@redhat.com)
- 734882 - User-Agent header in katello-cli and custom error messages
  (inecas@redhat.com)
- Merge branch 'uebercert' (dmitri@redhat.com)
- 736247 - correct error message on unauthorized access (inecas@redhat.com)
- system-tests - script for generating code coverage (inecas@redhat.com)
- adding copyright and modeline to our spec files (lzap+git@redhat.com)
- packagegroups - cli system test helpers methods to separate file
  (inecas@redhat.com)
- 737563 - adding more rhsm system testing (lzap+git@redhat.com)
- 737563 - improving rhsm system testing (lzap+git@redhat.com)
- 737563 - adding more rhsm system testing (lzap+git@redhat.com)
- 737563 - adding more rhsm system tests (lzap+git@redhat.com)
- cli coverage - added --cover-inclusive to get report for all files and not
  only for those with tests. Helps finding holes in the coverage.
  (tstrachota@redhat.com)
- system tests - added check for existing test suites (tstrachota@redhat.com)
- templates cli - fix for typo in route (tstrachota@redhat.com)
- templates api - route for listing templates in an environment
  (tstrachota@redhat.com)
- added test coverage target to katello cli Makefile (dmitri@redhat.com)
- packagegroups - name cli tests using convention (inecas@redhat.com)
- packagegroups-templates - CLI for package group categories in templates
  (inecas@redhat.com)
- system-tests - refactor - use function for getting repo_id
  (inecas@redhat.com)
- packagegroups-templates - CLI system tests (inecas@redhat.com)
- packagegroups-templates - CLI for package groups in templates
  (inecas@redhat.com)
- 737591 - format function was missing positional arguments method str.format
  requires positional argument specifiers in Python < 2.7
  (tstrachota@redhat.com)
- system tests - temporarily disabled deleting a provider in provider_import
  test until we fix the bug (tstrachota@redhat.com)
- cli - removed unused imports (tstrachota@redhat.com)
- Change the default client config to work with thin/apache
  (bkearney@redhat.com)
- Merge branch 'master' into thin (mmccune@redhat.com)
- Merge branch 'master' into thin (mmccune@redhat.com)
- CLI - client.conf - update path to default to /katello
  (bbuckingham@redhat.com)
- ueber cert - adding cli support (lzap+git@redhat.com)

* Thu Sep 08 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.10-1
- cli - deprecated 'has_key' replaced by 'in'
- cli - reindented .py scripts
- system tests - fix for unknown parameter in template test removed
  --environment parameter that is no longer used in template update action
- templates cli - typo in function parameter
- cli unittests - tests for template command + mock utility can now set also
  None as return value
- template cli - removed environment option from create/update actions -
  affected actions: import, create, update, update_content - environment option
  in promote action made required
- packagegroups - don't print curl output in system test

* Tue Sep 06 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.9-1
- cli - bumping cli version because of tito bug

* Tue Sep 06 2011 Lukas Zapletal <lzap+git@redhat.com>
- system test - moving cli_tests into cli/test-system
- Fix missing import in CLI
- Cli unit tests for package group categories
- Cli unit tests for package groups
- Cli support for package groups and package group categories
- 730358 - repo discovery now uses asynchronous tasks - the route has been
  changed to /organizations/ID/repositories/discovery/
- Move the cli over to the public zanata server
- cli packages - listing now same as rpm -q for system packages
- 735038 - Storing an option as root fails when .katello does not exist
- cli - disabled two pylint false alarms
- cli - new behaviour of verbose/grep output switching - for printing single
  item verbose is default - for printing collection of items grep is default -
  can be forced by flags -v, -g or in the config file
- repo cli - parameter --repo_id renamed to --id to make the cli uniform
- cli - fix for format_date returning only current time
- cli tests - files renamed according to pattern COMMAND_ACTION_test.py
- cli tests - provider status test
- cli tests - fixed typo in product status options test
- cli tests - fixed test for provider sync
- provider sync status - cli + api
- cli tests - repo status
- cli - fix for key error in getting error details from async tasks
- Refactor providers - remove unused routes

* Wed Aug 31 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.7-1
- Scope products by readability scope
- Refactor - move providers from OrganziationController

* Mon Aug 29 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.6-1
- cli - fixes for several typos
- cli tests - removed call of nonexisting function
- cli - product and repo uses AsyncTask
- cli - changeset promotion fix
- fix for cli issues with removed cp_id
- cli tests - product promote 2
- cli tests - product promote
- cli tests - product status
- cli tests - product sync
- cli tests - tests for listing and creation use common test data
- cli tests - test data
- product cli - fix for using wrong field from hash
- cli tests - product list
- cli tests - added mocking for printer to utils
- products cli - now displaying provider name
- sync cli - sync format functions refactoring
- products cli - fixed commands according to recent changes
- products cli - added action status
- cli repo status - displaying synchronization progress
- cli - asynchronous tasks refactored
- repo status - repo now defined also by org,product,env and name
- katello-cli - storing options to client-options.conf
- katello-cli - adding LICENSE and README with unit test info
- katelli-cli spec changelog cleanup
- 723308 - verbose environment information should list names not ids
- simple puppet scripts
- cli unittests - fix in testing parameters 2
- cli unittests - fix in testing parameters tests were using stored values from
  config files
- repo cli - all '--repo' renamed to '--name' to make the paramaters consistent
  accross the cli
- fix for cli repo sync failing when sync was unsuccessful
- cli test utils - renamed variable
- cli unit tests for repo sync + cli test utils
- more tests for provider sync cli
- added provider sync tests for cli
- fixed failing product creation tests for cli
- Merge branch 'master' of ssh://git.fedorahosted.org/git/katello
- Get translations in for the cli
- repo sync - check for syncing only repos in locker
- Automatic commit of package [katello-cli] release [0.1.5-1].
- 731446 - more variable name fixes

* Thu Aug 18 2011 Mike McCune <mmccune@redhat.com> 0.1.5-1
- periodic retag of the cli package

* Mon Aug 01 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.4-1
- spec - rpmlint cleanup
- Added api support for activation keys
- Turn on package updating
- Bug 725719 - Simple CLI tests are failing with -s parameter
- Bug 726416 - Katello-cli is failing on some terminals

* Tue Jul 26 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.3-1
- redhat provider - changing rhn to redhat in the cli
- spec - fixing files section of katello-cli
- spec - adding katello-cli package initial version

* Mon Jul 25 2011 Lukas Zapletal <lzap+git@redhat.com> 0.1.2-1
- spec - fixing files section of katello-cli

* Mon Jul 25 2011 Lukas Zapletal 0.1.1-1
- initial version

