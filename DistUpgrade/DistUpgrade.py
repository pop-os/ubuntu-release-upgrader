#!/usr/bin/python2.4

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk
import gtk.glade

import apt
from UpdateManager.Common.SimpleGladeApp import SimpleGladeApp
from UpdateManager.GtkProgress import GtkOpProgress
from SoftwareProperties.aptsources import SourcesList, SourceEntry
from gettext import gettext as _

class DistUpgradeProgress(object):
    pass


class DistUpgradeView(object):
    " abstraction for the upgrade view "
    def __init__(self):
        pass
    def getOpCacheProgress(self):
        " return a OpProgress() subclass for the given graphic"
        return apt.progress.OpProgress()
    def updateStatus(self, msg):
        """ update the current status of the distUpgrade based
            on the current view
        """
        pass
    def askYesNoQuestion(self,msg):
        pass

class GtkDistUpgradeView(DistUpgradeView,SimpleGladeApp):
    " gtk frontend of the distUpgrade tool "
    def __init__(self):
        # FIXME: i18n must be somewhere relative do this dir
        SimpleGladeApp.__init__(self, "DistUpgrade.glade",
                                None, domain="update-manager")
        self._opCacheProgress = GtkOpProgress(self.progressbar_cache)
    def getOpCacheProgress(self):
        return self._opCacheProgress
    def updateStatus(self, msg):
        self.label_status = "<b>%s</b>" % msg

class DistUpgradeControler(object):
    def __init__(self, distUpgradeView):
        self._view = distUpgradeView

    def sanityCheck(self):
        pass

    def updateSourcesList(self, fromDist, to):
        sources = SourcesList()
        sources.backup()

        # this must map, i.e. second in "from" must be the second in "to"
        # (but they can be different, so in theory we could exchange
        #  component names here)
        fromDists = [fromDist,
                     fromDist+"-security",
                     fromDist+"-updates",
                     fromDist+"-backports"
                    ]
        toDists = [to,
                   to+"-security",
                   to+"-updates",
                   to+"-backports"
                   ]

        # list of valid mirrors that we can add
        valid_mirrors = ["http://archive.ubuntu.com/ubuntu",
                         "http://security.ubuntu.com/ubuntu"]
        
        for entry in sources:
            # check if it's a mirror (or offical site)
            for mirror in valid_mirrors:
                if sources.is_mirror(mirror,entry.uri):
                    if entry.dist in fromDists:
                        entry.dist = toDists[fromDists.index(entry.dist)]
                    else:
                        # disable all entries that are official but don't
                        # point to the "from" dist
                        entry.disabled = True
                else:
                    # disable non-official entries that point to dist
                    if entry.dist == fromDist:
                        entry.disabled = True
        # write!
        sources.save()

    def breezyUpgrade(self):
        # sanity check (check for ubuntu-desktop, brokenCache etc)
        self._view.updateStatus(_("Checking the system"))
        self.sanityCheck()

        # update sources.list
        self._view.updateStatus(_("Updating repository information"))
        self.updateSourcesList(fromDist="hoary",to="breezy")

        # then update the package index files


        # then open the cache
        self._view.updateStatus(_("Reading cache"))
        self._cache = apt.Cache(self._view.getOpCacheProgress())

        # do pre-upgrade stuff

        # calc the dist-upgrade and see if the removals are ok/expected

        # do the dist-upgrade

        # do post-upgrade stuff

        # done, ask for reboot

    def run(self):
        self.breezyUpgrade()


if __name__ == "__main__":
    view = GtkDistUpgradeView()
    app = DistUpgradeControler(view)
    app.run()
