/*
  ==============================================================================

    This file was auto-generated!

  ==============================================================================
*/

#ifndef MAINCOMPONENT_H_INCLUDED
#define MAINCOMPONENT_H_INCLUDED

#include "../JuceLibraryCode/JuceHeader.h"
#include "ecosystem.h"
#include "ExperimentInterface.h"
#include <boost/filesystem.hpp>



class MapComponent;
class ExperimentComponent;
class ExperimentInterface;
class SettingsComponent;

class MainTabbedComponent : public TabbedComponent
{
public:
    MainTabbedComponent(TabbedButtonBar::Orientation orientation);
    void setSettingsComponentPointer(SettingsComponent* settings_component);
    void currentTabChanged (int newCurrentTabIndex, const String &newCurrentTabName);
private:
    SettingsComponent* _settings_component;
};

//==============================================================================
/*
    Main component of the application
*/
class MainContentComponent   : public Component,
                               private Timer
{
public:
    /** @brief Instance of ExperimentInterface. Where the Ecosystem is running.
     */
    ExperimentInterface* experiment_interface;
    
    /** @brief Indicates the experiment has changed and must be redrawn
     */
    bool experiment_has_changed;
    
    /** @brief True if ecosystem is running
     */
    bool running;
    // Public methods (documentation in MainComponent.cpp)
    MainContentComponent();
    ~MainContentComponent();
    void paint (Graphics&);
    void resized();
    void loadEcosystemInterface(ExperimentInterface* ei);
private:
    /** @brief Pointer to MapComponent (where ecosystem is rendered)
     */
    MapComponent* _map_component;
    
    /** @brief Pointer to ExperimentComponent (where experiment is loaded)
     */
    ExperimentComponent* _experiment_component;
    
    /** @brief Pointer to SettingsComponent (where settings are shown)
     */
    SettingsComponent* _settings_component;
    
    //---
    ScopedPointer<MainTabbedComponent> _tabbedComponent;
    void timerCallback();

    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainContentComponent)
};


#endif  // MAINCOMPONENT_H_INCLUDED
